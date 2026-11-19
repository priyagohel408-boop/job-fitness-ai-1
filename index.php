<?php
// index.php - landing page. No sidebar, uses the top navigation bar instead.
$pageTitle = 'Home';
$showSidebar = false;
include __DIR__ . '/includes/header.php';
?>
<section class="hero">
  <h1>Find the career that fits you.</h1>
  <p>Job Fitness AI predicts careers that suit your profile, then shows how well your current skills match the career you choose.</p>
  <div class="actions">
    <a class="btn" href="paths.php">Find My Career</a>
    <a class="btn btn-light" href="how-it-works.php">Explore Career Paths</a>
  </div>
</section>

<section class="section">
  <h2>Two ways to start</h2>
  <div class="grid-2">
    <div class="card"><h3>I Have a Dream Career</h3><p>Pick a career you want. We compare your skills with what it needs.</p><a class="btn btn-small" href="dream-career.php">Assess My Career</a></div>
    <div class="card dark"><h3>Recommend Me a Career</h3><p>Share your profile. A trained model suggests a career for you.</p><a class="btn btn-small" href="profile.php">Find My Career</a></div>
  </div>
</section>

<section class="section">
  <h2>How the system works</h2>
  <ol class="steps">
    <li>You enter a profile or choose a dream career.</li>
    <li>The backend checks your input.</li>
    <li>A Random Forest model predicts a career (recommendation path).</li>
    <li>O*NET provides the skills that career needs.</li>
    <li>You see matched skills, missing skills and a fitness score.</li>
  </ol>
</section>

<section class="section">
  <h2>What you get</h2>
  <div class="grid-3">
    <div class="card"><h3>Career prediction</h3><p>A model-generated career suggestion based on your profile.</p></div>
    <div class="card"><h3>Skill matching</h3><p>Your skills compared with the skills of a career.</p></div>
    <div class="card"><h3>Career fitness</h3><p>A score and learning priorities for the skills you lack.</p></div>
  </div>
</section>
<?php include __DIR__ . '/includes/footer.php'; ?>
