<?php
// includes/header.php - top of every page. Set $pageTitle and $showSidebar BEFORE including.
require_once __DIR__ . '/api.php';
$pageTitle   = $pageTitle ?? 'Job Fitness AI';
$showSidebar = $showSidebar ?? true;
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= e($pageTitle) ?> | Job Fitness AI</title>
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="layout <?= $showSidebar ? 'with-sidebar' : '' ?>">
<?php if ($showSidebar) { include __DIR__ . '/sidebar.php'; } else { ?>
  <header class="topnav">
    <a class="brand" href="index.php"><span class="logo"></span>Job Fitness AI</a>
    <nav>
      <a href="how-it-works.php">How it works</a>
      <a href="paths.php">Career paths</a>
      <a class="btn btn-small" href="paths.php">Find My Career</a>
    </nav>
  </header>
<?php } ?>
<main class="content">
