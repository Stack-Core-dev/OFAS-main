package com.ofas.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.ofas.app.ui.screen.DeviceCheckScreen
import com.ofas.app.ui.screen.FieldSelectionScreen
import com.ofas.app.ui.screen.HomeScreen
import com.ofas.app.ui.screen.PhotoCaptureScreen
import com.ofas.app.ui.screen.ReviewScreen
import com.ofas.app.ui.screen.SuccessScreen
import com.ofas.app.ui.screen.auth.AuthScreen
import com.ofas.app.ui.screen.FaceVerificationScreen
import com.ofas.app.ui.screen.auth.FaceEnrollmentScreen

@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = NavRoutes.AUTH
    ) {
        composable(NavRoutes.AUTH) {
            AuthScreen(navController = navController)
        }

        composable(NavRoutes.HOME) {
            HomeScreen(
                onStartVisit = {
                    navController.navigate(NavRoutes.DEVICE_CHECK)
                },
                onSync = {},
                onSettings = {}
            )
        }

        composable(NavRoutes.DEVICE_CHECK) {
            DeviceCheckScreen(
                onContinue = {
                    navController.navigate(NavRoutes.FIELD_SELECTION)
                }
            )
        }

        composable(NavRoutes.FIELD_SELECTION) {
            FieldSelectionScreen(
                onFieldSelected = { field, surveyorId ->
                    navController.navigate(NavRoutes.faceVerification(surveyorId, field.id))
                }
            )
        }

        composable(NavRoutes.FACE_ENROLLMENT) {
            FaceEnrollmentScreen(
                onEnrolled = {
                    navController.navigate(NavRoutes.HOME) {
                        popUpTo(NavRoutes.AUTH) { inclusive = true }
                    }
                },
                onCancel = {
                    navController.popBackStack()
                }
            )
        }

        composable(
            route = NavRoutes.FACE_VERIFICATION,
            arguments = listOf(
                navArgument("surveyorId") { type = NavType.StringType },
                navArgument("fieldId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val surveyorId = backStackEntry.arguments?.getString("surveyorId") ?: ""
            val fieldId = backStackEntry.arguments?.getString("fieldId") ?: ""
            FaceVerificationScreen(
                surveyorId = surveyorId,
                fieldId = fieldId,
                onVerified = {
                    navController.navigate(NavRoutes.photoCapture(surveyorId, fieldId, "Field"))
                }
            )
        }

        composable(
            route = NavRoutes.PHOTO_CAPTURE,
            arguments = listOf(
                navArgument("surveyorId") { type = NavType.StringType },
                navArgument("fieldId") { type = NavType.StringType },
                navArgument("fieldName") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val surveyorId = backStackEntry.arguments?.getString("surveyorId") ?: ""
            val fieldId = backStackEntry.arguments?.getString("fieldId") ?: ""
            val fieldName = backStackEntry.arguments?.getString("fieldName") ?: ""
            PhotoCaptureScreen(
                surveyorId = surveyorId,
                fieldId = fieldId,
                fieldName = fieldName,
                onFinish = {
                    navController.navigate(NavRoutes.review("visit_data"))
                }
            )
        }

        composable(
            route = NavRoutes.REVIEW,
            arguments = listOf(
                navArgument("visitData") { type = NavType.StringType }
            )
        ) {
            ReviewScreen(
                onSubmit = {
                    navController.navigate(NavRoutes.SUCCESS) {
                        popUpTo(NavRoutes.HOME)
                    }
                },
                onCancel = {
                    navController.popBackStack()
                }
            )
        }

        composable(NavRoutes.SUCCESS) {
            SuccessScreen(
                onDone = {
                    navController.navigate(NavRoutes.HOME) {
                        popUpTo(NavRoutes.HOME) { inclusive = true }
                    }
                }
            )
        }
    }
}
