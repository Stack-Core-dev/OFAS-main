// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
      fullName: json['fullName'] as String,
      role: json['role'] as String,
      isActive: json['isActive'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      lastLoginAt: json['lastLoginAt'] == null
          ? null
          : DateTime.parse(json['lastLoginAt'] as String),
      phoneNumber: json['phoneNumber'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      mfaEnabled: json['mfaEnabled'] as bool? ?? false,
      passkeyEnabled: json['passkeyEnabled'] as bool? ?? false,
    );

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'email': instance.email,
      'fullName': instance.fullName,
      'role': instance.role,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'lastLoginAt': instance.lastLoginAt?.toIso8601String(),
      'phoneNumber': instance.phoneNumber,
      'avatarUrl': instance.avatarUrl,
      'mfaEnabled': instance.mfaEnabled,
      'passkeyEnabled': instance.passkeyEnabled,
    };

AuthTokens _$AuthTokensFromJson(Map<String, dynamic> json) => AuthTokens(
      accessToken: json['accessToken'] as String,
      refreshToken: json['refreshToken'] as String,
      expiresIn: (json['expiresIn'] as num).toInt(),
      tokenType: json['tokenType'] as String,
    );

Map<String, dynamic> _$AuthTokensToJson(AuthTokens instance) =>
    <String, dynamic>{
      'accessToken': instance.accessToken,
      'refreshToken': instance.refreshToken,
      'expiresIn': instance.expiresIn,
      'tokenType': instance.tokenType,
    };

LoginRequest _$LoginRequestFromJson(Map<String, dynamic> json) => LoginRequest(
      username: json['username'] as String,
      password: json['password'] as String,
      totpCode: json['totpCode'] as String?,
    );

Map<String, dynamic> _$LoginRequestToJson(LoginRequest instance) =>
    <String, dynamic>{
      'username': instance.username,
      'password': instance.password,
      'totpCode': instance.totpCode,
    };

MfaSetupResponse _$MfaSetupResponseFromJson(Map<String, dynamic> json) =>
    MfaSetupResponse(
      secret: json['secret'] as String,
      qrCodeUrl: json['qrCodeUrl'] as String,
      backupCodes: (json['backupCodes'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$MfaSetupResponseToJson(MfaSetupResponse instance) =>
    <String, dynamic>{
      'secret': instance.secret,
      'qrCodeUrl': instance.qrCodeUrl,
      'backupCodes': instance.backupCodes,
    };

PasskeyRegistrationOptions _$PasskeyRegistrationOptionsFromJson(
        Map<String, dynamic> json) =>
    PasskeyRegistrationOptions(
      challenge: json['challenge'] as String,
      rpId: json['rpId'] as String,
      rpName: json['rpName'] as String,
      userId: json['userId'] as String,
      userName: json['userName'] as String,
      userDisplayName: json['userDisplayName'] as String,
      pubKeyCredParams: (json['pubKeyCredParams'] as List<dynamic>)
          .map((e) =>
              PublicKeyCredentialParameter.fromJson(e as Map<String, dynamic>))
          .toList(),
      authenticatorSelection: AuthenticatorSelectionCriteria.fromJson(
          json['authenticatorSelection'] as Map<String, dynamic>),
      timeout: (json['timeout'] as num).toInt(),
    );

Map<String, dynamic> _$PasskeyRegistrationOptionsToJson(
        PasskeyRegistrationOptions instance) =>
    <String, dynamic>{
      'challenge': instance.challenge,
      'rpId': instance.rpId,
      'rpName': instance.rpName,
      'userId': instance.userId,
      'userName': instance.userName,
      'userDisplayName': instance.userDisplayName,
      'pubKeyCredParams': instance.pubKeyCredParams,
      'authenticatorSelection': instance.authenticatorSelection,
      'timeout': instance.timeout,
    };

PublicKeyCredentialParameter _$PublicKeyCredentialParameterFromJson(
        Map<String, dynamic> json) =>
    PublicKeyCredentialParameter(
      type: json['type'] as String,
      alg: (json['alg'] as num).toInt(),
    );

Map<String, dynamic> _$PublicKeyCredentialParameterToJson(
        PublicKeyCredentialParameter instance) =>
    <String, dynamic>{
      'type': instance.type,
      'alg': instance.alg,
    };

AuthenticatorSelectionCriteria _$AuthenticatorSelectionCriteriaFromJson(
        Map<String, dynamic> json) =>
    AuthenticatorSelectionCriteria(
      authenticatorAttachment: json['authenticatorAttachment'] as String,
      requireResidentKey: json['requireResidentKey'] as bool,
      userVerification: json['userVerification'] as String,
    );

Map<String, dynamic> _$AuthenticatorSelectionCriteriaToJson(
        AuthenticatorSelectionCriteria instance) =>
    <String, dynamic>{
      'authenticatorAttachment': instance.authenticatorAttachment,
      'requireResidentKey': instance.requireResidentKey,
      'userVerification': instance.userVerification,
    };
