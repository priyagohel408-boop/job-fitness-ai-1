<?php
// download.php - sends the latest assessment result as a PDF file.
// The PDF is built with plain PHP (no library, no JavaScript).
require_once __DIR__ . '/includes/api.php';   // also loads config.php and starts the session

// Use the result that results.php saved in the session.
$result = $_SESSION['result'] ?? null;
if (!$result) {
    header('Location: dream-career.php');      // nothing to download yet
    exit;
}

$career   = (string)($result['career'] ?? 'Career');
$score    = round((float)($result['fitness_score'] ?? 0), 1);
$matched  = skill_names($result['matched_skills'] ?? []);
$missing  = skill_names($result['missing_skills'] ?? []);

$roadmap = is_array($result['learning_roadmap'] ?? null)
    ? $result['learning_roadmap']
    : [];

$roadmapStages = is_array($roadmap['stages'] ?? null)
    ? $roadmap['stages']
    : [];

$capstoneProject = (string)($roadmap['capstone_project'] ?? '');

$roadmapNote = (string)($roadmap['note'] ?? '');

$total    = count($matched) + count($missing);
$matchPct = $total > 0 ? round(count($matched) / $total * 100) : 0;
$date     = date('d M Y');

// ---------------------------------------------------------------
// SimplePdf: a tiny PDF writer. It draws text and coloured boxes
// on A4 pages and starts a new page when the current one is full.
// ---------------------------------------------------------------
class SimplePdf
{
    private $pages = [];        // finished pages (each one is PDF drawing text)
    private $content = '';      // the page being drawn now
    private $y = 792;           // current vertical position (0 = bottom of page)
    private $left = 50;         // left margin
    private $width = 495;       // usable width between margins

    // Clean text so it is safe inside a PDF string.
    private function clean($text)
    {
        $text = preg_replace('/\s+/', ' ', (string)$text);
        $latin = false;
        if (function_exists('iconv')) {
            $converted = @iconv('UTF-8', 'Windows-1252//TRANSLIT//IGNORE', $text);
            if ($converted !== false) { $text = $converted; $latin = true; }
        }
        // Replace anything the standard PDF font cannot show with "?".
        $text = $latin ? preg_replace('/[^\x20-\x7E\xA0-\xFF]/', '?', $text)
                       : preg_replace('/[^\x20-\x7E]/', '?', $text);
        return str_replace(['\\', '(', ')'], ['\\\\', '\\(', '\\)'], $text);
    }

    private function num($n) { return number_format($n, 2, '.', ''); }

    private function color($rgb) { return $this->num($rgb[0]) . ' ' . $this->num($rgb[1]) . ' ' . $this->num($rgb[2]); }

    // Draw one line of text at an exact position.
    public function textAt($x, $y, $text, $size, $bold, $rgb)
    {
        $font = $bold ? 'F2' : 'F1';
        $this->content .= 'BT /' . $font . ' ' . $size . ' Tf ' . $this->color($rgb) . ' rg '
            . $this->num($x) . ' ' . $this->num($y) . ' Td (' . $this->clean($text) . ") Tj ET\n";
    }

    // Draw a filled rectangle.
    public function rect($x, $y, $w, $h, $rgb)
    {
        $this->content .= $this->color($rgb) . ' rg ' . $this->num($x) . ' ' . $this->num($y) . ' '
            . $this->num($w) . ' ' . $this->num($h) . " re f\n";
    }

    public function setY($y) { $this->y = $y; }

    public function gap($amount) { $this->y -= $amount; }

    // Start a new page.
    public function newPage()
    {
        $this->pages[] = $this->content;
        $this->content = '';
        $this->y = 792;
    }

    // Write a paragraph that wraps onto several lines.
    public function paragraph($text, $size, $bold, $rgb, $indent = 0)
    {
        $maxChars = max(10, (int)(($this->width - $indent) / ($size * 0.55)));
        // Wrap the plain text first, then clean each line for the PDF.
        $plain = preg_replace('/\s+/', ' ', (string)$text);
        $lines = explode("\n", wordwrap($plain, $maxChars, "\n", true));
        foreach ($lines as $line) {
            if ($this->y < 70) { $this->newPage(); }
            $font = $bold ? 'F2' : 'F1';
            $this->content .= 'BT /' . $font . ' ' . $size . ' Tf ' . $this->color($rgb) . ' rg '
                . $this->num($this->left + $indent) . ' ' . $this->num($this->y) . ' Td (' . $this->clean($line) . ") Tj ET\n";
            $this->y -= $size * 1.5;
        }
    }

    // A horizontal progress bar (0-100).
    public function bar($percent, $trackRgb, $fillRgb)
    {
        $percent = max(0, min(100, $percent));
        $this->rect($this->left, $this->y - 4, $this->width, 10, $trackRgb);
        if ($percent > 0) {
            $this->rect($this->left, $this->y - 4, $this->width * $percent / 100, 10, $fillRgb);
        }
        $this->y -= 24;
    }

    // Put every page together into one PDF file (returned as a string).
    public function output()
    {
        $this->pages[] = $this->content;
        $count = count($this->pages);

        $out = "%PDF-1.4\n";
        $offsets = [];
        $addObject = function ($number, $body) use (&$out, &$offsets) {
            $offsets[$number] = strlen($out);
            $out .= $number . " 0 obj\n" . $body . "\nendobj\n";
        };

        // Page objects are 5, 7, 9... and their content objects are 6, 8, 10...
        $kids = [];
        for ($i = 0; $i < $count; $i++) { $kids[] = (5 + 2 * $i) . ' 0 R'; }

        $addObject(1, '<< /Type /Catalog /Pages 2 0 R >>');
        $addObject(2, '<< /Type /Pages /Kids [' . implode(' ', $kids) . '] /Count ' . $count . ' >>');
        $addObject(3, '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');
        $addObject(4, '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');

        for ($i = 0; $i < $count; $i++) {
            $pageNo = 5 + 2 * $i;
            $contentNo = 6 + 2 * $i;
            $addObject($pageNo, '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
                . '/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ' . $contentNo . ' 0 R >>');
            $addObject($contentNo, '<< /Length ' . strlen($this->pages[$i]) . " >>\nstream\n"
                . $this->pages[$i] . "endstream");
        }

        // Cross-reference table tells the PDF reader where each object starts.
        $lastObject = 4 + 2 * $count;
        $xrefPosition = strlen($out);
        $out .= "xref\n0 " . ($lastObject + 1) . "\n0000000000 65535 f \n";
        for ($n = 1; $n <= $lastObject; $n++) {
            $out .= sprintf("%010d 00000 n \n", $offsets[$n]);
        }
        $out .= "trailer\n<< /Size " . ($lastObject + 1) . " /Root 1 0 R >>\nstartxref\n"
            . $xrefPosition . "\n%%EOF";
        return $out;
    }
}

// ---------------------------------------------------------------
// Build the report
// ---------------------------------------------------------------
$charcoal = [0.165, 0.157, 0.188];
$ink      = [0.15, 0.14, 0.17];
$muted    = [0.43, 0.42, 0.45];
$white    = [1, 1, 1];
$peach    = [0.94, 0.72, 0.60];
$track    = [0.89, 0.86, 0.81];
$green    = [0.40, 0.62, 0.40];
$red      = [0.80, 0.38, 0.32];

$pdf = new SimplePdf();

// Dark header band with the title
$pdf->rect(0, 752, 595, 90, $charcoal);
$pdf->textAt(50, 800, 'Job Fitness AI', 12, false, $peach);
$pdf->textAt(50, 770, 'Career Fitness Report', 22, true, $white);
$pdf->setY(725);

$pdf->paragraph('Date: ' . $date, 10, false, $muted);
$pdf->gap(6);
$pdf->paragraph($career, 18, true, $ink);
$pdf->gap(8);

// Fitness score and bar
$pdf->paragraph('Career Fitness Score', 10, false, $muted);
$pdf->gap(8);
$pdf->paragraph($score . ' / 100', 26, true, $ink);
$pdf->bar($score, $track, $peach);

// Skill match and bar
$pdf->paragraph('Skill match: ' . $matchPct . '% (' . count($matched) . ' of ' . $total . ' skills)', 11, false, $ink);
$pdf->gap(4);
$pdf->bar($matchPct, $track, $green);

// Matched skills
$pdf->gap(6);
$pdf->paragraph('Matched skills', 14, true, $green);
if ($matched) {
    foreach ($matched as $skill) { $pdf->paragraph('-  ' . $skill, 11, false, $ink, 10); }
} else {
    $pdf->paragraph('None', 11, false, $muted, 10);
}

// Missing skills
$pdf->gap(10);
$pdf->paragraph('Missing skills (learning priorities)', 14, true, $red);
if ($missing) {
    foreach ($missing as $number => $skill) { $pdf->paragraph(($number + 1) . '.  ' . $skill, 11, false, $ink, 10); }
} else {
    $pdf->paragraph('None', 11, false, $muted, 10);
}


/* Personalised Learning Roadmap */
$pdf->newPage();

$pdf->paragraph('Personalised Learning Roadmap', 18, true, $ink);
$pdf->gap(4);

$pdf->paragraph(
    'Career: ' . $career,
    11,
    false,
    $muted
);
$pdf->gap(6);

if (!empty($roadmapStages)) {
    foreach ($roadmapStages as $index => $stage) {
        if (!is_array($stage)) {
            continue;
        }

        $stageNumber = (int)($stage['stage'] ?? ($index + 1));
        $stageTitle = (string)($stage['title'] ?? 'Learning stage');

        // Stage heading
        $pdf->gap(8);
        $pdf->paragraph(
            'Stage ' . $stageNumber . ': ' . $stageTitle,
            13,
            true,
            $ink
        );

        // Skills to learn
        $stageSkills = is_array($stage['skills_to_learn'] ?? null)
            ? skill_names($stage['skills_to_learn'])
            : [];

        if ($stageSkills) {
            $pdf->paragraph(
                'Skills to learn:',
                10,
                true,
                $muted,
                10
            );

            foreach ($stageSkills as $skill) {
                $pdf->paragraph(
                    '- ' . $skill,
                    10,
                    false,
                    $ink,
                    18
                );
            }
        }

        // Learning objective
        if (!empty($stage['objective'])) {
            $pdf->gap(3);
            $pdf->paragraph(
                'Learning objective:',
                10,
                true,
                $muted,
                10
            );

            $pdf->paragraph(
                (string)$stage['objective'],
                10,
                false,
                $ink,
                10
            );
        }

        // Practice task
        if (!empty($stage['practice_task'])) {
            $pdf->gap(3);
            $pdf->paragraph(
                'Practice task:',
                10,
                true,
                $muted,
                10
            );

            $pdf->paragraph(
                (string)$stage['practice_task'],
                10,
                false,
                $ink,
                10
            );
        }

        $pdf->gap(5);
    }

    // Final practical project
    if ($capstoneProject !== '') {
        $pdf->gap(8);
        $pdf->paragraph(
            'Capstone Project',
            14,
            true,
            $green
        );

        $pdf->paragraph(
            $capstoneProject,
            11,
            false,
            $ink,
            10
        );
    }

    // Roadmap explanation
    if ($roadmapNote !== '') {
        $pdf->gap(10);
        $pdf->paragraph(
            'Roadmap note: ' . $roadmapNote,
            9,
            false,
            $muted
        );
    }
} else {
    $pdf->paragraph(
        'No learning roadmap was available for this assessment.',
        11,
        false,
        $muted
    );
}



// Optional note from the backend
if (!empty($result['message'])) {
    $pdf->gap(10);
    $pdf->paragraph('Note: ' . $result['message'], 10, false, $muted);
}

$pdfData = $pdf->output();

// Safe file name, e.g. career-fitness-data-scientist.pdf
$slug = trim(preg_replace('/[^a-z0-9]+/', '-', strtolower($career)), '-');
$fileName = 'career-fitness-' . ($slug !== '' ? $slug : 'report') . '.pdf';

header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="' . $fileName . '"');
header('Content-Length: ' . strlen($pdfData));
header('X-Content-Type-Options: nosniff');
echo $pdfData;
exit;