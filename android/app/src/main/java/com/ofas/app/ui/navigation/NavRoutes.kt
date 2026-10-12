package com.ofas.app.ui.navigation

object NavRoutes {
    const val AUTH = "auth"
    const val HOME = "home"
    const val DEVICE_CHECK = "device_check"
    const val FIELD_SELECTION = "field_selection"
    const val FACE_VERIFICATION = "face_verification/{surveyorId}/{fieldId}"
    const val FACE_ENROLLMENT = "face_enrollment"
    const val PHOTO_CAPTURE = "photo_capture/{surveyorId}/{fieldId}/{fieldName}"
    const val REVIEW = "review/{visitData}"
    const val SUCCESS = "success"

    fun faceVerification(surveyorId: String, fieldId: String) =
        "face_verification/$surveyorId/$fieldId"

    fun photoCapture(surveyorId: String, fieldId: String, fieldName: String) =
        "photo_capture/$surveyorId/$fieldId/$fieldName"

    fun review(visitData: String) = "review/$visitData"
}
