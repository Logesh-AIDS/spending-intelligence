package com.spending.intelligence.presentation.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ── Brand Colors ─────────────────────────────────────────────────────────────
val PrimaryBlue = Color(0xFF1A56DB)
val PrimaryBlueDark = Color(0xFF1340B0)
val PrimaryBlueLight = Color(0xFF4B7EF5)
val AccentGreen = Color(0xFF00C896)
val AccentRed = Color(0xFFFF4D6A)
val AccentOrange = Color(0xFFFF8C42)
val AccentPurple = Color(0xFF7C3AED)
val AccentYellow = Color(0xFFFFBF00)
val BackgroundLight = Color(0xFFF0F4FF)
val SurfaceLight = Color(0xFFFFFFFF)
val CardBlue = Color(0xFFE8EEFF)
val CardGreen = Color(0xFFE0FBF4)
val CardRed = Color(0xFFFFEBEE)
val CardPurple = Color(0xFFF3EEFF)

// Gradient colors
val GradientStart = Color(0xFF1A56DB)
val GradientEnd = Color(0xFF7C3AED)
val GradientGreenStart = Color(0xFF00C896)
val GradientGreenEnd = Color(0xFF00A3FF)

private val LightColorScheme = lightColorScheme(
    primary = PrimaryBlue,
    onPrimary = Color.White,
    primaryContainer = CardBlue,
    onPrimaryContainer = PrimaryBlueDark,
    secondary = AccentGreen,
    onSecondary = Color.White,
    secondaryContainer = CardGreen,
    tertiary = AccentPurple,
    background = BackgroundLight,
    surface = SurfaceLight,
    surfaceVariant = Color(0xFFF5F7FF),
    error = AccentRed,
    onBackground = Color(0xFF0D1B4B),
    onSurface = Color(0xFF0D1B4B),
    onSurfaceVariant = Color(0xFF6B7DB3),
    outline = Color(0xFFD0D8F0),
)

@Composable
fun SpendingTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = Typography(),
        content = content
    )
}
