package com.ofas.app.di

import android.content.Context
import androidx.room.Room
import com.ofas.data.database.OFASDatabase
import com.ofas.data.repository.FieldRepository
import com.ofas.data.repository.SurveyorRepository
import com.ofas.data.repository.VisitRepository
import com.ofas.data.sync.ApiService
import com.ofas.security.keystore.KeyManager
import com.ofas.data.trail.TrailManager
import com.ofas.app.repository.AuthRepository
import com.ofas.data.face.FaceVerifier
import com.ofas.core.util.DeviceInfo
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    private const val BASE_URL = "http://10.10.4.133:5000/"

    @Provides
    @Singleton
    fun provideDatabase(@dagger.hilt.android.qualifiers.ApplicationContext context: Context): OFASDatabase {
        return Room.databaseBuilder(
            context,
            OFASDatabase::class.java,
            "ofas.db"
        ).build()
    }

    @Provides
    @Singleton
    fun provideFieldRepository(database: OFASDatabase): FieldRepository {
        return FieldRepository(database.fieldDao())
    }

    @Provides
    @Singleton
    fun provideSurveyorRepository(database: OFASDatabase): SurveyorRepository {
        return SurveyorRepository(database.surveyorDao())
    }

    @Provides
    @Singleton
    fun provideVisitRepository(database: OFASDatabase): VisitRepository {
        return VisitRepository(database.visitDao())
    }

    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        val moshi = Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideKeyManager(@dagger.hilt.android.qualifiers.ApplicationContext context: Context): KeyManager {
        return KeyManager.getInstance(context)
    }

    @Provides
    @Singleton
    fun provideTrailManager(
        @dagger.hilt.android.qualifiers.ApplicationContext context: Context,
        database: OFASDatabase,
        keyManager: KeyManager
    ): TrailManager {
        return TrailManager.getInstance(context, database, keyManager)
    }

    @Provides
    @Singleton
    fun provideFaceVerifier(
        @dagger.hilt.android.qualifiers.ApplicationContext context: Context,
        keyManager: KeyManager
    ): FaceVerifier {
        return FaceVerifier.getInstance(context, keyManager)
    }

    @Provides
    @Singleton
    fun provideDeviceInfo(@dagger.hilt.android.qualifiers.ApplicationContext context: Context): DeviceInfo {
        return DeviceInfo(context)
    }

    @Provides
    @Singleton
    fun provideAuthRepository(@dagger.hilt.android.qualifiers.ApplicationContext context: Context): AuthRepository {
        return AuthRepository(context)
    }
}