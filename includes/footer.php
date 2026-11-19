<?php // includes/footer.php - bottom of every page; closes tags opened in header.php. ?>
</main>
<footer class="footer">
  <div>
    <strong>Job Fitness AI</strong>
    <p>A career guidance project that predicts suitable careers and measures how well your skills match them.</p>
  </div>
  <div>
    <p>Team: <?= e(TEAM_MEMBERS) ?></p>
    <p>Guide: <?= e(PROJECT_GUIDE) ?></p>
    <p><?= e(DEPARTMENT) ?>, <?= e(INSTITUTION) ?></p>
    <p>Academic year: <?= e(ACADEMIC_YEAR) ?></p>
  </div>
  <p class="copy">&copy; <?= date('Y') ?> Job Fitness AI. Academic project.</p>
</footer>
</div>
</body>
</html>
