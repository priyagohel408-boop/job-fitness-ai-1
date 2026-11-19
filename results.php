
<?php
// results.php - Career fitness assessment using FastAPI /career-fitness

$pageTitle = 'Career fitness';
require_once __DIR__ . '/includes/api.php';

$pageTitle = 'Career fitness';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$errors = [];
$result = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $career = trim($_POST['career'] ?? '');

// Support both the checkbox form and the comma-separated text form.
if (isset($_POST['selected_skills']) && is_array($_POST['selected_skills'])) {
    $selectedSkills = array_values(array_unique(array_filter(
        array_map('trim', $_POST['selected_skills']),
        fn($skill) => $skill !== ''
    )));
} else {
    $skillsInput = trim($_POST['skills'] ?? '');
    $selectedSkills = split_list($skillsInput);
}

    $careerLength = function_exists('mb_strlen')
        ? mb_strlen($career, 'UTF-8')
        : strlen($career);

    if ($career === '' || $careerLength > 100) {
        $errors[] = 'Please enter a career (up to 100 characters).';
    }   
if ($mode === 'career_fitness' && empty($selectedSkills)) {
    $errors[] = 'Please select at least one skill from the checklist.';
}

    if (!$errors) {
        // FastAPI expects "career" and "selected_skills".
        $endpoint = defined('ENDPOINT_CAREER_FITNESS')
            ? ENDPOINT_CAREER_FITNESS
            : '/career-fitness';

       $res = api_request('POST', $endpoint, [
    'career' => $career,
    'occupation_code' => trim($_POST['occupation_code'] ?? ''),
    'selected_skills' => $selectedSkills
]);

        if (empty($res['ok'])) {
            $errors[] = $res['error'] ?? 'The backend request failed.';
        } else {
            $data = $res['data'] ?? [];
            $fitness = $data['fitness'] ?? [];

            if (($data['matched'] ?? false) !== true) {
                $errors[] = $data['message']
                    ?? 'No matching career was found. Please try another career.';
            } elseif (!is_array($fitness) ||
                      !isset($fitness['matched_skills']) ||
                      !isset($fitness['missing_skills'])) {
                $errors[] = 'The backend response has an unexpected format. Check the API response.';
            } else {
                $matched = skill_names($fitness['matched_skills']);
                $missing = skill_names($fitness['missing_skills']);

                // Use the backend score if provided.
                $score = $fitness['fitness_score']
                    ?? $fitness['score']
                    ?? $fitness['match_percentage']
                    ?? null;

                // Fallback: calculate a percentage from matched/missing skills.
                if (!is_numeric($score)) {
                    $totalSkills = count($matched) + count($missing);
                    $score = $totalSkills > 0
                        ? (count($matched) / $totalSkills) * 100
                        : 0;
                }

                
            $result = [
                'career' => $career,
                'fitness_score' => max(0, min(100, (float)$score)),
                'matched_skills' => $matched,
                'missing_skills' => $missing,
                'essential_missing' => [],
                'optional_missing' => [],
                'message' => $data['message'] ?? '',
                'learning_roadmap' => $data['learning_roadmap'] ?? null
            ];


                $_SESSION['result'] = $result;
            }
        }
    }
} else {
    // Do not display an old result when the page is opened directly.
    unset($_SESSION['result']);
}

if ($errors) {
    $result = null;
}

include __DIR__ . '/includes/header.php';
?>

<?php if ($errors): ?>

    <h1>We could not complete the assessment</h1>

    <?php foreach ($errors as $err): ?>
        <div class="alert"><?= e($err) ?></div>
    <?php endforeach; ?>

    <div class="actions">
        <a class="btn" href="dream-career.php">Try again</a>
        <a class="btn btn-light" href="paths.php">Back to paths</a>
    </div>

<?php elseif ($result): ?>

    <?php
    $score = $result['fitness_score'];
    $matched = $result['matched_skills'];
    $missing = $result['missing_skills'];

    $total = count($matched) + count($missing);
    $matchPct = $total > 0
        ? round(count($matched) / $total * 100)
        : 0;

    $priorities = array_values(array_unique(array_merge(
        $result['essential_missing'],
        $missing
    )));
    ?>

    <h1>Career fitness: <?= e($result['career']) ?></h1>

    <div class="grid-2">
        <div class="card dark">
            <p class="muted-light">Career Fitness Score</p>
            <div class="score">
                <?= e(round($score, 1)) ?><small>/100</small>
            </div>
            <div class="bar">
                <span style="width: <?= e($score) ?>%"></span>
            </div>
        </div>

        <div class="card">
            <p class="muted">Skill match</p>
            <div class="score">
                <?= e($matchPct) ?>%
                <small>(<?= count($matched) ?> of <?= $total ?>)</small>
            </div>
            <div class="bar">
                <span style="width: <?= e($matchPct) ?>%"></span>
            </div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3>Matched skills</h3>
            <div class="badges">
                <?php foreach ($matched as $skill): ?>
                    <span class="badge ok"><?= e($skill) ?></span>
                <?php endforeach; ?>

                <?php if (!$matched): ?>
                    <p class="muted">No matched skills.</p>
                <?php endif; ?>
            </div>
        </div>

        <div class="card">
            <h3>Missing skills</h3>
            <div class="badges">
                <?php foreach ($missing as $skill): ?>
                    <span class="badge miss"><?= e($skill) ?></span>
                <?php endforeach; ?>

                <?php if (!$missing): ?>
                    <p class="muted">No missing skills.</p>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <div class="card">
        <h3>Learning priorities</h3>

        <?php if ($priorities): ?>
            <ol>
                <?php foreach (array_slice($priorities, 0, 8) as $skill): ?>
                    <li>Learn <?= e($skill) ?></li>
                <?php endforeach; ?>
            </ol>
        <?php else: ?>
            <p>You match all the skills returned for this career.</p>
        <?php endif; ?>
    </div>

    <div class="card">
        <h3>Summary</h3>
        <p>
            For <?= e($result['career']) ?>, you matched
            <?= count($matched) ?> of <?= $total ?> skills and received
            a fitness score of <?= e(round($score, 1)) ?>/100.
            <?= $missing
                ? 'Focus on the missing skills above to improve your fit.'
                : 'Your skills cover the listed requirements.' ?>
        </p>

        <?php if ($result['message'] !== ''): ?>
            <p class="muted"><?= e($result['message']) ?></p>
        <?php endif; ?>
    </div>


    <?php
    $roadmap = $result['learning_roadmap'] ?? null;
    $roadmapStages = is_array($roadmap)
        && is_array($roadmap['stages'] ?? null)
        ? $roadmap['stages']
        : [];
    ?>

    <div class="card roadmap-card">
        <div class="roadmap-heading">
            <div>
                <p class="muted roadmap-eyebrow">YOUR NEXT STEPS</p>
                <h2>Personalised Learning Roadmap</h2>
                <p class="muted">
                    Build your skills step by step for
                    <?= e($result['career']) ?>.
                </p>
            </div>
            <span class="roadmap-status">
                <?= !empty($roadmapStages) ? 'In progress' : 'No gaps found' ?>
            </span>
        </div>

        <?php if (!empty($roadmapStages)): ?>

            <div class="roadmap-timeline">
                <?php foreach ($roadmapStages as $index => $stage): ?>
                    <article class="roadmap-stage">
                        <div class="roadmap-number">
                            <?= e($stage['stage'] ?? ($index + 1)) ?>
                        </div>

                        <div class="roadmap-stage-content">
                            <h3><?= e($stage['title'] ?? 'Learning stage') ?></h3>

                            <?php if (!empty($stage['skills_to_learn'])
                                && is_array($stage['skills_to_learn'])): ?>
                                <h4>Skills to learn</h4>
                                <div class="badges roadmap-skills">
                                    <?php foreach ($stage['skills_to_learn'] as $skill): ?>
                                        <span class="badge miss">
                                            <?= e($skill) ?>
                                        </span>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>

                            <?php if (!empty($stage['objective'])): ?>
                                <p>
                                    <strong>Learning objective:</strong><br>
                                    <?= e($stage['objective']) ?>
                                </p>
                            <?php endif; ?>

                            <?php if (!empty($stage['practice_task'])): ?>
                                <p>
                                    <strong>Practice task:</strong><br>
                                    <?= e($stage['practice_task']) ?>
                                </p>
                            <?php endif; ?>
                        </div>
                    </article>
                <?php endforeach; ?>
            </div>

            <?php if (!empty($roadmap['capstone_project'])): ?>
                <div class="capstone-box">
                    <p class="muted roadmap-eyebrow">FINAL PRACTICAL PROJECT</p>
                    <h3>Capstone Project</h3>
                    <p><?= e($roadmap['capstone_project']) ?></p>
                </div>
            <?php endif; ?>

        <?php else: ?>

            <p>
                No roadmap stages were returned. You may already match all
                the skills in this assessment, or the backend did not provide
                a roadmap. Review the missing skills above.
            </p>

        <?php endif; ?>

        <?php if (!empty($roadmap['note'])): ?>
            <p class="muted roadmap-note">
                <?= e($roadmap['note']) ?>
            </p>
        <?php endif; ?>
    </div>


    <div class="actions">
        <a class="btn" href="download.php">Download PDF</a>
        <a class="btn" href="index.php">Back to home</a>
        <a class="btn btn-light" href="dream-career.php">Select another career</a>
        <a class="btn btn-light"
           href="dream-career.php?career=<?= urlencode($result['career']) ?>">
            Repeat assessment
        </a>
    </div>

<?php else: ?>

    <h1>No assessment available</h1>
    <p>Please select a career and submit your skills first.</p>
    <a class="btn" href="dream-career.php">Start assessment</a>

<?php endif; ?>

<?php include __DIR__ . '/includes/footer.php'; ?>
