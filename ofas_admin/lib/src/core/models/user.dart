import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String username;
  final String email;
  final String fullName;
  final String role;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? lastLoginAt;
  final String? phoneNumber;
  final String? avatarUrl;
  final bool mfaEnabled;
  final bool passkeyEnabled;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isActive,
    required this.createdAt,
    this.lastLoginAt,
    this.phoneNumber,
    this.avatarUrl,
    this.mfaEnabled = false,
    this.passkeyEnabled = false,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}

@JsonSerializable()
class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final String tokenType;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    required this.tokenType,
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) => _$AuthTokensFromJson(json);
  Map<String, dynamic> toJson() => _$AuthTokensToJson(this);
}

@JsonSerializable()
class LoginRequest {
  final String username;
  final String password;
  final String? totpCode;

  LoginRequest({
    required this.username,
    required this.password,
    this.totpCode,
  });

  factory LoginRequest.fromJson(Map<String, dynamic> json) => _$LoginRequestFromJson(json);
  Map<String, dynamic> toJson() => _$LoginRequestToJson(this);
}

@JsonSerializable()
class MfaSetupResponse {
  final String secret;
  final String qrCodeUrl;
  final List<String> backupCodes;

  MfaSetupResponse({
    required this.secret,
    required this.qrCodeUrl,
    required this.backupCodes,
  });

  factory MfaSetupResponse.fromJson(Map<String, dynamic> json) => _$MfaSetupResponseFromJson(json);
  Map<String, dynamic> toJson() => _$MfaSetupResponseToJson(this);
}

@JsonSerializable()
class PasskeyRegistrationOptions {
  final String challenge;
  final String rpId;
  final String rpName;
  final String userId;
  final String userName;
  final String userDisplayName;
  final List<PublicKeyCredentialParameter> pubKeyCredParams;
  final AuthenticatorSelectionCriteria authenticatorSelection;
  final int timeout;

  PasskeyRegistrationOptions({
    required this.challenge,
    required this.rpId,
    required this.rpName,
    required this.userId,
    required this.userName,
    required this.userDisplayName,
    required this.pubKeyCredParams,
    required this.authenticatorSelection,
    required this.timeout,
  });

  factory PasskeyRegistrationOptions.fromJson(Map<String, dynamic> json) => _$PasskeyRegistrationOptionsFromJson(json);
  Map<String, dynamic> toJson() => _$PasskeyRegistrationOptionsToJson(this);
}

@JsonSerializable()
class PublicKeyCredentialParameter {
  final String type;
  final int alg;

  PublicKeyCredentialParameter({
    required this.type,
    required this.alg,
  });

  factory PublicKeyCredentialParameter.fromJson(Map<String, dynamic> json) => _$PublicKeyCredentialParameterFromJson(json);
  Map<String, dynamic> toJson() => _$PublicKeyCredentialParameterToJson(this);
}

@JsonSerializable()
class AuthenticatorSelectionCriteria {
  final String authenticatorAttachment;
  final bool requireResidentKey;
  final String userVerification;

  AuthenticatorSelectionCriteria({
    required this.authenticatorAttachment,
    required this.requireResidentKey,
    required this.userVerification,
  });

  factory AuthenticatorSelectionCriteria.fromJson(Map<String, dynamic> json) => _$AuthenticatorSelectionCriteriaFromJson(json);
  Map<String, dynamic> toJson() => _$AuthenticatorSelectionCriteriaToJson(this);
}