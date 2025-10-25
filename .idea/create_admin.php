<?php
require 'config.php';

// Hash the password once and store it
$username = 'admin';
$plain_password = 'admin123';
$hash = password_hash($plain_password, PASSWORD_DEFAULT);

$stmt = $conn->prepare("INSERT INTO users (username, password_hash) VALUES (?, ?)");
$stmt->bind_param("ss", $username, $hash);
$stmt->execute();

echo "Admin created with username: $username and password: $plain_password";
