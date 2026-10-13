from typing import Optional, Tuple, List
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from geoalchemy2 import functions as geofunc
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from .models import Field, Visit
from .config import config


def create_point(lat: float, lon: float, srid: int = 4326) -> WKTElement:
    return WKTElement(f'POINT({lon} {lat})', srid=srid)


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def is_within_field_radius(
    visit_lat: float, visit_lon: float, visit_accuracy: float,
    field_lat: float, field_lon: float, field_radius: float,
    tolerance: float = 10.0
) -> Tuple[bool, float]:
    distance = distance_meters(visit_lat, visit_lon, field_lat, field_lon)
    effective_radius = field_radius + visit_accuracy + tolerance
    return distance <= effective_radius, distance


def is_within_field_radius_postgis(
    db: Session, visit_lat: float, visit_lon: float, visit_accuracy: float,
    field_id: str, tolerance: float = 10.0
) -> Tuple[bool, Optional[float]]:
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        return False, None

    if not field.center_point:
        # Fall back to the haversine implementation using the stored
        # latitude/longitude when the PostGIS geometry point is missing (e.g.
        # rows created before center_point was populated).
        return is_within_field_radius(
            visit_lat, visit_lon, visit_accuracy,
            field.center_lat, field.center_lon, field.radius_meters, tolerance
        )
    
    visit_point = create_point(visit_lat, visit_lon)
    
    distance = db.query(
        geofunc.ST_Distance(
            field.center_point.ST_Transform(3857),
            visit_point.ST_Transform(3857)
        )
    ).scalar()
    
    if distance is None:
        return False, None
    
    effective_radius = field.radius_meters + visit_accuracy + tolerance
    return distance <= effective_radius, distance


def get_fields_near_point(
    db: Session, lat: float, lon: float, radius_meters: float,
    limit: int = 50
) -> List[Field]:
    point = create_point(lat, lon)
    return db.query(Field).filter(
        geofunc.ST_DWithin(
            Field.center_point.ST_Transform(3857),
            point.ST_Transform(3857),
            radius_meters
        ),
        Field.is_active == True
    ).limit(limit).all()


def validate_visit_location(
    db: Session, visit_lat: float, visit_lon: float, visit_accuracy: float,
    field_id: str
) -> Tuple[bool, float, str]:
    field = db.query(Field).filter(Field.id == field_id, Field.is_active == True).first()
    if not field:
        return False, 0.0, "Field not found or inactive"
    
    tolerance = config['default']().FIELD_RADIUS_TOLERANCE
    is_within, distance = is_within_field_radius_postgis(
        db, visit_lat, visit_lon, visit_accuracy, field_id, tolerance
    )
    
    if not is_within:
        return False, distance or 0.0, \
            f"Visit location {distance:.1f}m from field center, " \
            f"exceeds radius {field.radius_meters}m + accuracy {visit_accuracy}m + tolerance {tolerance}m"
    
    return True, distance or 0.0, "Location valid"


def validate_point_within_field(
    db: Session, lat: float, lon: float, accuracy: Optional[float],
    field_id: str, label: str = "Point"
) -> Tuple[bool, float, str]:
    """Validate an evidence point (field photo / selfie) against the assigned
    field radius so captured evidence must be inside the farm boundary."""
    field = db.query(Field).filter(Field.id == field_id, Field.is_active == True).first()
    if not field:
        return False, 0.0, "Field not found or inactive"

    tolerance = config['default']().FIELD_RADIUS_TOLERANCE
    effective_accuracy = accuracy or 0.0
    is_within, distance = is_within_field_radius(
        lat, lon, effective_accuracy,
        field.center_lat, field.center_lon, field.radius_meters, tolerance
    )
    distance = distance or 0.0

    if not is_within:
        return False, distance, \
            f"{label} location {distance:.1f}m from field center, " \
            f"exceeds radius {field.radius_meters}m + accuracy {effective_accuracy}m + tolerance {tolerance}m"

    return True, distance, "Location valid"


def get_field_center_wkt(field: Field) -> str:
    if field.center_point:
        shape = to_shape(field.center_point)
        return f"POINT({shape.x} {shape.y})"
    return f"POINT({field.center_lon} {field.center_lat})"


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, degrees, sin, cos, atan2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    bearing = atan2(y, x)
    return (degrees(bearing) + 360) % 360


def calculate_speed(
    lat1: float, lon1: float, time1: float,
    lat2: float, lon2: float, time2: float
) -> Optional[float]:
    if time2 <= time1:
        return None
    distance = distance_meters(lat1, lon1, lat2, lon2)
    time_diff = time2 - time1
    return distance / time_diff