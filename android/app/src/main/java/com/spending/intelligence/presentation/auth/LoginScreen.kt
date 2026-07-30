package com.spending.intelligence.presentation.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.*
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.presentation.theme.*

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit,
    viewModel: AuthViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var showPassword by remember { mutableStateOf(false) }

    LaunchedEffect(state.isSuccess) { if (state.isSuccess) onLoginSuccess() }

    Column(
        modifier = Modifier.fillMaxSize()
            .background(Brush.verticalGradient(listOf(Color(0xFF0D1B4B), PrimaryBlue, Color(0xFF1A56DB))))
    ) {
        // Top section with logo
        Box(
            modifier = Modifier.fillMaxWidth().weight(0.38f),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("💰", fontSize = 56.sp)
                Spacer(Modifier.height(8.dp))
                Text("SpendControl", fontSize = 28.sp, fontWeight = FontWeight.ExtraBold,
                    color = Color.White)
                Text("AI-Powered Finance", fontSize = 14.sp,
                    color = Color.White.copy(alpha = 0.7f))
            }
        }

        // Bottom card
        Box(
            modifier = Modifier.fillMaxWidth().weight(0.62f)
                .clip(RoundedCornerShape(topStart = 32.dp, topEnd = 32.dp))
                .background(BackgroundLight)
        ) {
            Column(Modifier.fillMaxSize().padding(28.dp)) {
                Text("Welcome Back", fontSize = 24.sp, fontWeight = FontWeight.Bold,
                    color = Color(0xFF0D1B4B))
                Text("Sign in to continue", fontSize = 14.sp, color = Color(0xFF6B7DB3))
                Spacer(Modifier.height(24.dp))

                // Email field
                OutlinedTextField(
                    value = email, onValueChange = { email = it },
                    label = { Text("Email address") },
                    leadingIcon = { Icon(Icons.Default.Email, null, tint = PrimaryBlue) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = PrimaryBlue,
                        unfocusedBorderColor = Color(0xFFD0D8F0),
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White
                    )
                )
                Spacer(Modifier.height(14.dp))

                // Password field
                OutlinedTextField(
                    value = password, onValueChange = { password = it },
                    label = { Text("Password") },
                    leadingIcon = { Icon(Icons.Default.Lock, null, tint = PrimaryBlue) },
                    trailingIcon = {
                        IconButton(onClick = { showPassword = !showPassword }) {
                            Icon(
                                if (showPassword) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                null, tint = Color(0xFF6B7DB3)
                            )
                        }
                    },
                    visualTransformation = if (showPassword) VisualTransformation.None else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = PrimaryBlue,
                        unfocusedBorderColor = Color(0xFFD0D8F0),
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White
                    )
                )

                // Error
                state.error?.let { err ->
                    Spacer(Modifier.height(10.dp))
                    Row(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
                            .background(CardRed).padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Warning, null, tint = AccentRed,
                            modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(8.dp))
                        val axiosErr = err
                        Text(axiosErr, color = AccentRed, fontSize = 13.sp)
                    }
                }

                Spacer(Modifier.height(24.dp))

                // Sign in button
                Button(
                    onClick = { viewModel.login(email, password) },
                    modifier = Modifier.fillMaxWidth().height(52.dp),
                    enabled = !state.isLoading,
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                ) {
                    if (state.isLoading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp, color = Color.White)
                    } else {
                        Text("Sign In", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                    }
                }

                Spacer(Modifier.height(16.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                    Text("Don't have an account? ", fontSize = 14.sp, color = Color(0xFF6B7DB3))
                    TextButton(onClick = onNavigateToRegister, contentPadding = PaddingValues(0.dp)) {
                        Text("Sign Up", fontSize = 14.sp, fontWeight = FontWeight.Bold,
                            color = PrimaryBlue)
                    }
                }
            }
        }
    }
}
