<?php
// dream-career.php - Path A: O*NET search, occupation choice, then skill checklist.
$pageTitle = 'Dream career';
require_once __DIR__ . '/includes/api.php';
$mode = trim($_GET['mode'] ?? $_POST['mode'] ?? 'career_fitness');
$career = trim($_GET['career'] ?? $_POST['career'] ?? '');
$search = trim($_GET['q'] ?? '');

if ($search === '' && $mode === 'career_recommendation' && $career !== '') {
    $search = $career;
}

$code = trim($_GET['occupation_code'] ?? $_POST['occupation_code'] ?? '');
$errors = [];
$searchNote = '';
$occupations = [];
$skills = [];
$occupationTitle = $career;
$description = '';

if ($code !== '' && $career !== '') {
    $res = api_request('POST', ENDPOINT_CAREER_SKILLS, [
        'career' => $career,
        'occupation_code' => $code,
    ]);
    if (!$res['ok']) {
        $errors[] = $res['error'];
    } elseif (needs_occupation_choice($res['data'])) {
        $occupations = occupations_from($res['data']);
        $searchNote = (string)($res['data']['message'] ?? 'Please select an occupation.');
        $code = '';
    } elseif (empty($res['data']['matched'])) {
        $errors[] = (string)($res['data']['message'] ?? 'No matching occupation was found.');
    } else {
        $occupationTitle = (string)(($res['data']['occupation']['title'] ?? $career));
        $code = (string)(($res['data']['occupation']['code'] ?? $code));
        $description = (string)($res['data']['description'] ?? '');
        $skills = skill_names($res['data']['skills'] ?? []);
        if (!$skills) {
            $errors[] = (string)($res['data']['skill_extraction_note'] ?? 'This occupation was found, but no O*NET skill names could be extracted.');
        }
    }
} elseif ($search !== '') {
    $res = api_request('POST', ENDPOINT_CAREER_SEARCH, ['career' => $search]);

    if (!$res['ok']) {
        $searchNote = $res['error'];
    } elseif (empty($res['data']['matched'])) {
        $searchNote = (string)($res['data']['message'] ?? 'No matching careers found. Try another title.');
    } else {
        $occupations = occupations_from($res['data']);

        if (!$occupations) {
            $searchNote = 'No matching careers found. Try another title.';
        } elseif ($mode === 'career_recommendation') {
            // Automatically use the first matching occupation.
            $code = (string)$occupations[0]['code'];
            $career = (string)$occupations[0]['title'];

            $res = api_request('POST', ENDPOINT_CAREER_SKILLS, [
                'career' => $career,
                'occupation_code' => $code,
            ]);

            if (!$res['ok']) {
                $errors[] = $res['error'];
            } elseif (!empty($res['data']['matched'])) {
                $occupationTitle = (string)($res['data']['occupation']['title'] ?? $career);
                $code = (string)($res['data']['occupation']['code'] ?? $code);
                $description = (string)($res['data']['description'] ?? '');
                $skills = skill_names($res['data']['skills'] ?? []);

                if (!$skills) {
                    $errors[] = (string)($res['data']['skill_extraction_note'] ?? 'No skills were returned for this occupation.');
                }
            } else {
                $errors[] = (string)($res['data']['message'] ?? 'Could not load skills for this career.');
            }
        }
    }
}
include __DIR__ . '/includes/header.php';
?>
<h1>Assess my dream career</h1>
<p class="muted">Search O*NET, choose an occupation, then check the skills you already have. The fitness score is calculated from those checked O*NET skills.</p>
<?php foreach ($errors as $err): ?><div class="alert"><?= e($err) ?></div><?php endforeach; ?>

<?php if ($mode !== 'career_recommendation'): ?>
<form method="get" class="card form">
      <label>Search careers<input type="text" name="q" value="<?= e($search) ?>" placeholder="e.g. Data Scientist" maxlength="150"></label>
  <div class="actions"><button class="btn btn-light" type="submit">Search</button></div>
  <?php if ($searchNote): ?><p class="muted"><?= e($searchNote) ?></p><?php endif; ?>
  <?php if ($occupations && $code === ''): ?>
    <div class="badges">
      <?php foreach ($occupations as $item): ?>
        <a class="badge" href="dream-career.php?career=<?= urlencode($item['title']) ?>&occupation_code=<?= urlencode($item['code']) ?>"><?= e($item['title']) ?></a>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>
</form>
<?php endif; ?>
<?php if ($code !== '' && $skills): ?>
<form method="post" action="results.php" class="card form">
<input type="hidden" name="mode" value="<?= e($mode) ?>">
<input type="hidden" name="flow" value="<?= $mode === 'career_recommendation' ? 'path_b' : 'path_a' ?>">
  <input type="hidden" name="career" value="<?= e($occupationTitle) ?>">
  <input type="hidden" name="occupation_code" value="<?= e($code) ?>">
  <h2><?= e($occupationTitle) ?></h2>
  <?php if ($description): ?><p class="muted"><?= e($description) ?></p><?php endif; ?>
  <p>Check every skill you already have. Unchecked skills are treated as gaps.</p>

<div class="checklist">
  <?php foreach ($skills as $skill): ?>
    <label class="skill-option">
      <input
        type="checkbox"
        name="selected_skills[]"
        value="<?= e($skill) ?>"
      >
      <span><?= e($skill) ?></span>
    </label>
  <?php endforeach; ?>
</div>

  <div class="actions"><button class="btn" type="submit">Calculate Career Fitness</button></div>
<p class="muted">Select the skills you currently have. Unchecked skills will be treated as skill gaps.</p>
</form>
<?php endif; ?>
<?php include __DIR__ . '/includes/footer.php'; ?>
