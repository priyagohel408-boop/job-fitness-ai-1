<?php
// includes/sidebar.php - left navigation, included by header.php.
$current = basename($_SERVER['PHP_SELF']);
$links = [
    'index.php'         => 'Home',
    'paths.php'         => 'Choose a path',
    'dream-career.php'  => 'Dream career',
    'profile.php'       => 'Recommend a career',
    'results.php'       => 'Latest results',
    'how-it-works.php'  => 'How it works',
];
?>
<aside class="sidebar">
  <a class="brand" href="index.php"><span class="logo"></span>Job Fitness AI</a>
  <nav>
    <?php foreach ($links as $file => $label): ?>
      <a href="<?= e($file) ?>" class="<?= $current === $file ? 'active' : '' ?>"><?= e($label) ?></a>
    <?php endforeach; ?>
  </nav>
</aside>
