<?php
// profile.php - Path B form. Validates in PHP, calls POST /predict-career.
$pageTitle = 'Student profile';
require_once __DIR__ . '/includes/api.php';

$errors = [];
$old = $_POST;
$genders = ['Male', 'Female', 'Other'];
$levels = ['Fresher', 'Intermediate', 'Advanced'];
$workModes = ['Remote', 'Onsite', 'Hybrid'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $profile = student_profile_from_input($_POST);
    $errors = validate_student_profile($profile);

    if (!$errors) {
        $res = api_request('POST', ENDPOINT_PREDICT, $profile);
        if (!$res['ok']) {
            $errors[] = $res['error'];
        } elseif (!api_has_fields($res['data'], ['recommended_career'])) {
            $errors[] = 'The backend response did not include a recommended career.';
        } else {
            $_SESSION['profile'] = $profile;
            $_SESSION['recommendation'] = $res['data'];
            header('Location: recommendations.php');
            exit;
        }
    }
}

function old($key) {
    global $old;
    return e($old[$key] ?? '');
}

include __DIR__ . '/includes/header.php';
?>
<h1>Tell us about yourself</h1>
<p class="muted">These fields match the Random Forest model features. Separate lists with commas. Nothing is stored in a database.</p>
<?php foreach ($errors as $err): ?><div class="alert"><?= e($err) ?></div><?php endforeach; ?>
<form method="post" class="card form">
  <label>Age *<input type="number" name="Age" min="13" max="100" value="<?= old('Age') ?>" required></label>
  <label>Gender *
    <select name="Gender" required><option value="">Choose...</option>
    <?php foreach ($genders as $o): ?><option <?= ($old['Gender'] ?? '') === $o ? 'selected' : '' ?>><?= e($o) ?></option><?php endforeach; ?>
    </select></label>
  <label>Education *<input type="text" name="Education" placeholder="Computer Science" value="<?= old('Education') ?>" required></label>
  <label>Degree *<input type="text" name="Degree" placeholder="Computer Science" value="<?= old('Degree') ?>" required></label>
  <label>CGPA (0-10) *<input type="number" step="0.01" min="0" max="10" name="CGPA" value="<?= old('CGPA') ?>" required></label>
  <label>Experience level *
    <select name="Experience_Level" required><option value="">Choose...</option>
    <?php foreach ($levels as $o): ?><option <?= ($old['Experience_Level'] ?? '') === $o ? 'selected' : '' ?>><?= e($o) ?></option><?php endforeach; ?>
    </select></label>
  <label>Years of experience *<input type="number" step="0.5" min="0" max="60" name="Years_of_Experience" value="<?= old('Years_of_Experience') !== '' ? old('Years_of_Experience') : '0' ?>" required></label>
  <label>Programming languages<input type="text" name="Programming_Languages" placeholder="Python, SQL" value="<?= old('Programming_Languages') ?>"></label>
  <label>Technical skills *<textarea name="Skills" rows="3" placeholder="MySQL, NumPy, Power BI" required><?= old('Skills') ?></textarea></label>
  <label>Certifications<input type="text" name="Certifications" placeholder="Google Data Analytics" value="<?= old('Certifications') ?>"></label>
  <label>Area of interest *<input type="text" name="Interest" placeholder="Data Science" value="<?= old('Interest') ?>" required></label>
  <label>Soft skills<input type="text" name="Soft_Skills" placeholder="Communication, Problem Solving" value="<?= old('Soft_Skills') ?>"></label>
  <label>Preferred work mode *
    <select name="Preferred_Work_Mode" required><option value="">Choose...</option>
    <?php foreach ($workModes as $m): ?><option <?= ($old['Preferred_Work_Mode'] ?? '') === $m ? 'selected' : '' ?>><?= e($m) ?></option><?php endforeach; ?>
    </select></label>
  <label>Resume score (0-100) *<input type="number" step="0.1" min="0" max="100" name="Resume_Score" value="<?= old('Resume_Score') ?>" required></label>
  <label>Coding test score (0-100) *<input type="number" step="0.1" min="0" max="100" name="Coding_Test_Score" value="<?= old('Coding_Test_Score') ?>" required></label>
  <label>Interview score (0-100) *<input type="number" step="0.1" min="0" max="100" name="Interview_Score" value="<?= old('Interview_Score') ?>" required></label>
  <div class="actions"><button class="btn" type="submit">Recommend My Career</button><a class="btn btn-light" href="paths.php">Back</a></div>
</form>
<?php include __DIR__ . '/includes/footer.php'; ?>
