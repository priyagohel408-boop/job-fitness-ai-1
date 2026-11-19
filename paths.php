<?php
// paths.php - the student picks Path A or Path B.
$pageTitle = 'Choose a path';
include __DIR__ . '/includes/header.php';
?>
<h1>Choose your path</h1>
<div class="grid-2">
  <div class="card">
    <h2>I Have a Dream Career</h2>
    <p>I already know which career I want to pursue.</p>
    <a class="btn" href="dream-career.php">Assess My Career</a>
  </div>
  <div class="card dark">
    <h2>Recommend Me a Career</h2>
    <p>Help me discover careers that may suit my profile.</p>
    <a class="btn" href="profile.php">Find My Career</a>
  </div>
</div>
<?php include __DIR__ . '/includes/footer.php'; ?>
