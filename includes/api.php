<?php
// Shared helpers for all pages. Save this file as UTF-8 without BOM.
require_once __DIR__ . '/../config.php';

function e($text): string {
    return htmlspecialchars((string)$text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function api_fail(string $message): array {
    return ['ok' => false, 'data' => null, 'error' => $message];
}

function format_api_detail($detail): string {
    if (is_string($detail)) {
        return $detail;
    }
    if (!is_array($detail)) {
        return 'The backend rejected the request.';
    }

    $parts = [];
    foreach ($detail as $item) {
        if (is_string($item)) {
            $parts[] = $item;
            continue;
        }
        if (!is_array($item)) {
            continue;
        }
        $msg = (string)($item['msg'] ?? '');
        $loc = '';
        if (isset($item['loc']) && is_array($item['loc'])) {
            $names = [];
            foreach (array_slice($item['loc'], 1) as $part) {
                if (is_scalar($part)) {
                    $names[] = (string)$part;
                }
            }
            $loc = implode('.', $names);
        }
        $text = trim($loc . ' ' . $msg);
        if ($text !== '') {
            $parts[] = $text;
        }
    }

    if ($parts) {
        return implode('; ', $parts);
    }
    $encoded = json_encode($detail, JSON_UNESCAPED_UNICODE);
    return $encoded !== false ? $encoded : 'The backend rejected the request.';
}

function api_request(string $method, string $path, array $data = []): array {
    if (!function_exists('curl_init')) {
        return api_fail('PHP cURL is not enabled. Enable extension=curl in your active php.ini, then restart PHP.');
    }

    $method = strtoupper($method);
    $url = rtrim(API_BASE_URL, '/') . '/' . ltrim($path, '/');
    if ($method === 'GET' && $data) {
        $url .= '?' . http_build_query($data);
    } elseif (!in_array($method, ['GET', 'POST'], true)) {
        return api_fail('Unsupported HTTP method.');
    }

    $options = [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => API_TIMEOUT,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => ['Accept: application/json', 'Content-Type: application/json'],
    ];
    if ($method === 'POST') {
        $payload = json_encode($data, JSON_UNESCAPED_UNICODE);
        if ($payload === false) {
            return api_fail('Could not encode the request as JSON.');
        }
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $payload;
    }

    $ch = curl_init($url);
    if ($ch === false) {
        return api_fail('Could not initialize the backend request.');
    }
    curl_setopt_array($ch, $options);
    $body = curl_exec($ch);
    $errno = curl_errno($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if ($errno === CURLE_OPERATION_TIMEDOUT) {
        return api_fail('The backend took too long to respond. Please try again.');
    }
    if ($errno !== 0 || $body === false) {
        return api_fail('Cannot reach the backend. Make sure FastAPI is running at ' . API_BASE_URL . '.');
    }
    if (trim($body) === '') {
        return api_fail("The backend returned an empty response (HTTP $status).");
    }

    $json = json_decode($body, true);
    if (!is_array($json)) {
        return api_fail("The backend response was not valid JSON (HTTP $status).");
    }
    if ($status < 200 || $status >= 300) {
        return api_fail('Backend error (HTTP ' . $status . '): ' . format_api_detail($json['detail'] ?? $body));
    }
    return ['ok' => true, 'data' => $json, 'error' => ''];
}

function api_has_fields(array $data, array $fields): bool {
    foreach ($fields as $field) {
        if (!array_key_exists($field, $data)) {
            return false;
        }
    }
    return true;
}

function split_list($text): array {
    if (is_array($text)) {
        $parts = $text;
    } elseif (!is_string($text)) {
        $parts = [];
    } else {
        $parts = preg_split('/[,\r\n]+/', $text) ?: [];
    }
    $clean = [];
    foreach ($parts as $part) {
        if (!is_scalar($part)) {
            continue;
        }
        $part = trim((string)$part);
        if ($part === '') {
            continue;
        }
        $length = function_exists('mb_strlen') ? mb_strlen($part, 'UTF-8') : strlen($part);
        if ($length > 80) {
            continue;
        }
        $key = function_exists('mb_strtolower') ? mb_strtolower($part, 'UTF-8') : strtolower($part);
        if (!isset($clean[$key])) {
            $clean[$key] = $part;
        }
    }
    return array_slice(array_values($clean), 0, 50);
}

function join_list($text): string {
    return implode(', ', split_list($text));
}

function skill_names($list): array {
    $names = [];
    foreach ((array)$list as $item) {
        $name = is_array($item) ? (string)($item['name'] ?? $item['title'] ?? $item['career'] ?? '') : (is_scalar($item) ? (string)$item : '');
        if (trim($name) !== '') {
            $names[] = trim($name);
        }
    }
    return array_values($names);
}

function occupations_from(array $data): array {
    $block = $data['occupation_result'] ?? $data;
    $items = $block['occupations'] ?? [];
    $out = [];
    foreach ((array)$items as $item) {
        if (!is_array($item)) {
            continue;
        }
        $code = trim((string)($item['code'] ?? ''));
        $title = trim((string)($item['title'] ?? ''));
        if ($code === '' || $title === '') {
            continue;
        }
        $out[] = ['code' => $code, 'title' => $title];
    }
    return $out;
}

function needs_occupation_choice(array $data): bool {
    $block = is_array($data['occupation_result'] ?? null) ? $data['occupation_result'] : $data;
    if (!empty($block['selection_required'])) {
        return true;
    }
    return empty($data['occupation']) && occupations_from($data) !== [];
}

function student_profile_from_input(array $src): array {
    return [
        'Age' => (int)($src['Age'] ?? 0),
        'Gender' => trim((string)($src['Gender'] ?? '')),
        'Education' => trim((string)($src['Education'] ?? '')),
        'Degree' => trim((string)($src['Degree'] ?? '')),
        'CGPA' => (float)($src['CGPA'] ?? 0),
        'Experience_Level' => trim((string)($src['Experience_Level'] ?? '')),
        'Years_of_Experience' => (float)($src['Years_of_Experience'] ?? 0),
        'Programming_Languages' => join_list($src['Programming_Languages'] ?? ''),
        'Skills' => join_list($src['Skills'] ?? ''),
        'Certifications' => join_list($src['Certifications'] ?? ''),
        'Interest' => trim((string)($src['Interest'] ?? '')),
        'Soft_Skills' => join_list($src['Soft_Skills'] ?? ''),
        'Preferred_Work_Mode' => trim((string)($src['Preferred_Work_Mode'] ?? '')),
        'Resume_Score' => (float)($src['Resume_Score'] ?? 0),
        'Coding_Test_Score' => (float)($src['Coding_Test_Score'] ?? 0),
        'Interview_Score' => (float)($src['Interview_Score'] ?? 0),
    ];
}

function validate_student_profile(array $profile): array {
    $errors = [];
    $genders = ['Male', 'Female', 'Other'];
    $levels = ['Fresher', 'Intermediate', 'Advanced'];
    $modes = ['Remote', 'Onsite', 'Hybrid'];

    if ($profile['Age'] < 13 || $profile['Age'] > 100) {
        $errors[] = 'Age must be a whole number from 13 to 100.';
    }
    if (!in_array($profile['Gender'], $genders, true)) {
        $errors[] = 'Please choose a gender.';
    }
    if ($profile['Education'] === '') {
        $errors[] = 'Please enter your education.';
    }
    if ($profile['Degree'] === '') {
        $errors[] = 'Please enter your degree.';
    }
    if ($profile['CGPA'] < 0 || $profile['CGPA'] > 10) {
        $errors[] = 'CGPA must be a number from 0 to 10.';
    }
    if (!in_array($profile['Experience_Level'], $levels, true)) {
        $errors[] = 'Please choose your experience level.';
    }
    if ($profile['Years_of_Experience'] < 0 || $profile['Years_of_Experience'] > 60) {
        $errors[] = 'Years of experience must be from 0 to 60.';
    }
    if ($profile['Skills'] === '') {
        $errors[] = 'Please list at least one technical skill.';
    }
    if ($profile['Interest'] === '') {
        $errors[] = 'Please enter your area of interest.';
    }
    if (!in_array($profile['Preferred_Work_Mode'], $modes, true)) {
        $errors[] = 'Please choose a preferred work mode.';
    }
    foreach (['Resume_Score' => 'Resume score', 'Coding_Test_Score' => 'Coding test score', 'Interview_Score' => 'Interview score'] as $key => $label) {
        if ($profile[$key] < 0 || $profile[$key] > 100) {
            $errors[] = $label . ' must be from 0 to 100.';
        }
    }
    return $errors;
}

function extract_fitness_view(array $data, string $fallbackCareer = ''): ?array {
    $fitness = is_array($data['fitness'] ?? null) ? $data['fitness'] : null;
    $score = $fitness['fitness_score'] ?? ($data['fitness_score'] ?? null);
    if ($score === null || $score === '') {
        return null;
    }

    $occupation = is_array($data['occupation'] ?? null) ? $data['occupation'] : [];
    $career = (string)($occupation['title'] ?? $data['career'] ?? $fallbackCareer);

    return [
        'career' => $career,
        'description' => is_string($data['description'] ?? null) ? $data['description'] : '',
        'message' => is_string($data['message'] ?? null) ? $data['message'] : (string)($fitness['message'] ?? ''),
        'fitness_score' => (float)$score,
        'matched_skills' => skill_names($fitness['matched_skills'] ?? ($data['checked_skills'] ?? [])),
        'missing_skills' => skill_names($fitness['missing_skills'] ?? ($data['unchecked_skills'] ?? [])),
        'path' => (string)($data['path'] ?? ''),
        'prediction' => is_array($data['prediction'] ?? null) ? $data['prediction'] : null,
    ];
}

function render_occupation_choices(array $occupations, string $career, string $action, array $hidden = []): void {
    if (!$occupations) {
        return;
    }
    echo '<div class="card"><h3>Select the closest O*NET occupation</h3>';
    echo '<p class="muted">The career title matched more than one occupation. Choose one to continue. Results come from O*NET, not from a local career list.</p>';
    foreach ($occupations as $item) {
        echo '<form method="post" action="' . e($action) . '" class="choice-row">';
        foreach ($hidden as $name => $value) {
            echo '<input type="hidden" name="' . e($name) . '" value="' . e($value) . '">';
        }
        echo '<input type="hidden" name="career" value="' . e($item['title']) . '">';
        echo '<input type="hidden" name="occupation_code" value="' . e($item['code']) . '">';
        echo '<button class="btn btn-light" type="submit">' . e($item['title']) . ' (' . e($item['code']) . ')</button>';
        echo '</form>';
    }
    echo '</div>';
}
