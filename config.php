<?php
// config.php - the ONLY place you change backend settings.
if (session_status() === PHP_SESSION_NONE) { session_start(); }

define('API_BASE_URL', 'https://job-fitness-ai-1.onrender.com');
define('API_TIMEOUT', 60);

define('ENDPOINT_PREDICT',       '/predict-career');
define('ENDPOINT_CAREER_SEARCH', '/careers/search');
define('ENDPOINT_CAREER_SKILLS', '/career-skills');
define('ENDPOINT_CAREER_FITNESS','/career-fitness');
define('ENDPOINT_ASSESS',        '/assess');

define('TEAM_MEMBERS', '[Tank Nirali, Chhaya Shraddha, Gohel Priya, Chudasama Sweta]');
define('PROJECT_GUIDE', '[I. H. Pathan]');
define('DEPARTMENT', '[Computer]');
define('INSTITUTION', '[GPP]');
define('ACADEMIC_YEAR', '[Winter-2026]');
