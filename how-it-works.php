<?php
// how-it-works.php - static explanation page.
$pageTitle = 'How it works';
include __DIR__ . '/includes/header.php';
?>
<h1>How Job Fitness AI works</h1>
<div class="card"><ol class="steps">
  <li>The student enters a profile or selects a dream career.</li>
  <li>The backend validates the input.</li>
  <li>A Random Forest model predicts a career when the recommendation path is used.</li>
  <li>The O*NET API supplies occupation information and skills.</li>
  <li>Skill matching finds matched and missing skills.</li>
  <li>The system calculates the Career Fitness Score.</li>
  <li>The app shows results and improvement guidance.</li>
</ol></div>
<div class="grid-2">
  <div class="card dark"><h3>Random Forest model</h3><p>Trained on a career dataset. It only predicts which career suits a profile. The dataset is not used to store student data.</p></div>
  <div class="card"><h3>O*NET API</h3><p>An external source of occupation details and required skills. It does not predict careers.</p></div>
</div>
<?php include __DIR__ . '/includes/footer.php'; ?>
