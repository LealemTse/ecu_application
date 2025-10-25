<?php
require 'config.php'; // this gives us $conn (MySQLi)

if ($argc < 3) {
    echo "Usage: php create_admin.php <username> <password>\n";
    exit(1);
}

$username = $argv[1];
$password = $argv[2];

// Hash the password
$password_hash = password_hash($password, PASSWORD_DEFAULT);

// Use prepared statement (MySQLi)
$stmt = $conn->prepare("INSERT INTO admins (username, password_hash) VALUES (?, ?)");
$stmt->bind_param("ss", $username, $password_hash);

if ($stmt->execute()) {
    echo "Admin user created: $username\n";
} else {
    echo "Error: " . $stmt->error . "\n";
}

$stmt->close();
$conn->close();
?>
