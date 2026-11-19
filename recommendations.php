<?php
// recommendations.php - shows the Random Forest result saved by profile.php.
$pageTitle = 'Recommendation';
require_once __DIR__ . '/includes/api.php';

if (empty($_SESSION['recommendation']['recommended_career']) || empty($_SESSION['profile'])) {
    header('Location: profile.php');
    exit;
}
$rec = $_SESSION['recommendation'];
$career = (string)$rec['recommended_career'];
$others = [];
if (!empty($rec['top_careers']) && is_array($rec['top_careers'])) {
    foreach ($rec['top_careers'] as $item) {
        if (!is_array($item)) {
            continue;
        }
        $name = trim((string)($item['career'] ?? ''));
        if ($name === '' || strcasecmp($name, $career) === 0) {
            continue;
        }
        $prob = $item['model_probability'] ?? null;
        $others[] = $prob === null ? $name : $name . ' (' . $prob . '%)';
    }
}
include __DIR__ . '/includes/header.php';
?>
<h1>Your recommended career</h1>
<div class="card dark">
  <p class="muted-light">Model-generated recommendation (Random Forest)</p>
  <h2><?= e($career) ?></h2>
  <p>This suggestion comes from a machine learning model trained on a career dataset. Use it as guidance, not a guarantee.</p>
</div>

<?php if ($others): ?>
<div class="card"><h3>Other careers suggested</h3>
  <div class="badges"><?php foreach ($others as $o): ?><span class="badge"><?= e($o) ?></span><?php endforeach; ?></div>
</div>
<?php endif; ?>

<div class="actions">
  <a class="btn"
     href="dream-career.php?career=<?= urlencode($career) ?>&mode=career_recommendation">
    Assess <?= e($career) ?>
  </a>

  <a class="btn btn-light" href="profile.php">
    Back to profile form
  </a>
</div>
<?php include __DIR__ . '/includes/footer.php'; ?>
