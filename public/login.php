<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Student Application Form LoginPage| ECUSTA-HLI University</title>
    <link href="https://fonts.googleapis.com/css?family=Montserrat&display=swap" rel="stylesheet">
    <style>
        /*Basic reset*/
        *{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: C059;
        }
        body {
            margin-top: 30px;
            margin-bottom: 50px;
            display: flex;
            justify-content: center;
            align-content: center;
            min-height: 100vh;
            background-color: #f5f5f5;
        }

        .login-wrapper {
            background-color: #fff;
            padding: 40px 30px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            width: 350px;
            text-align: center;
        }
        .login-logo img{
            width: 200px;
            margin-bottom: 20px;
        }
        .login-logo h1{
            font-size: 22px;
            margin-bottom: 20px;
            color: #333;
        }
        .login-wrapper input[type="text"],
        .login-wrapper input[type="password"]{
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        .login-wrapper button{
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        .log-wrapper button:hover{
            background-color: #0086b3;
            text-decoration: underline;
        }

        .login-wrapper .forgot-password{
            display: block;
            margin: 10px;
            font-size: 14px;
            color: #007bff;
            text-decoration: none;
        }
        .login-wrapper .forgot-password:hover{
            text-decoration: underline;
        }
        .login-divider {
            margin: 20px 0;
            height: 1px;
            background-color: #ddd
        }
        .login-instructions {
            font-size: 13px;
            text-align: left;
            color: #555;
        }


    </style>
</head>
<body>
<form method="POST" action="/login">
<div class="login-wrapper">
    <div class="login-logo">
        <img src="https://secure-exams.ecusta-hli.edu.et/pluginfile.php/1/core_admin/logo/0x200/1755767380/ecu.png" alt="Secure Exams Logo">
        <h1>ECUSTA-HLI Admin</h1>
    </div>

    <from action="#" method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log in</button>
    </from>

    `       <a href="https://mail.google.com/mail/u/0/#inbox?compose=CllgCJTLphmbqHJCdmBKpMVMsMrvNLnMngWbgpMHbLtpfswMkWzdHmNkDlrNZzKTBbDBDkljbSB" class="forgot-password">Lost Password?</a>

    <div class="login-divider"></div>

    <div class="login-instructions">
        <p>Manual logins (username/password) are only avalable to the Admins.</p>
        <ul>
            <li>The Admins can only login to this page. </li>
            <li>Attention Students: Unauthorized access to this page is strictly prohibited. <br>
                Any attempt to log in will be recorded, and your personal records may be reviewed by the administration.</li>
        </ul>
    </div>
</div>

</body>
</html>