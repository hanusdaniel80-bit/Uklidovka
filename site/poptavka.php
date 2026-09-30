<?php
/**
 * Poptávkový formulář -> e-mail do schránky firmy.
 * Běží na běžném webhostingu s PHP (Webglobe). Nic neukládá do databáze,
 * data neodcházejí k žádné třetí straně. Generováno z build.py.
 */
declare(strict_types=1);
date_default_timezone_set('Europe/Prague');

const TO_EMAIL   = 'info@uklid-pospisil.cz';        // kam poptávky chodí
const FROM_EMAIL = 'info@uklid-pospisil.cz';        // odesílatel: existující schránka na vlastní doméně
const SITE_NAME  = 'Úklid Pospíšil';
const THANKS_URL = 'dekujeme.html';
const MAX_PER_HOUR = 5;                // ochrana proti spamu: max. poptávek z jedné IP za hodinu

// Přihlášení do schránky pro odesílání přes SMTP (doporučuje Webglobe, méně spamu).
// Heslo NEPATŘÍ sem ani do gitu: zkopírujte poptavka-config.example.php jako
// poptavka-config.php (ideálně o složku výš, mimo web) a vyplňte ho tam.
// Bez konfigurace se použije PHP mail().
foreach ([__DIR__ . '/../poptavka-config.php', __DIR__ . '/poptavka-config.php'] as $cfg) {
    if (is_file($cfg)) { require $cfg; break; }
}

$SERVICES = [
    'uklid-domacnosti' => 'Úklid domácností',
    'uklid-firem' => 'Úklid firem a společných prostor',
    'uklid-po-stavbe' => 'Úklid po stavbě a malování',
    'myti-oken' => 'Mytí oken a žaluzií',
    'cisteni-kobercu-a-calouneni' => 'Čištění koberců, sedaček a matrací',
    'uklid-po-pojistne-udalosti' => 'Úklid po havárii a škodní události',
    'jine' => 'Něco jiného',
];

$wantsJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');

function finish(bool $ok, string $msg, bool $json, int $code = 200): never {
    if ($json) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $msg], JSON_UNESCAPED_UNICODE);
    } elseif ($ok) {
        header('Location: ' . THANKS_URL, true, 303);
    } else {
        http_response_code($code);
        header('Content-Type: text/html; charset=utf-8');
        echo '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
           . '<p style="font:18px system-ui;max-width:40em;margin:3em auto;padding:0 1em">'
           . htmlspecialchars($msg) . '<br><br><a href="kontakt.html">Zpět na formulář</a></p>';
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: kontakt.html', true, 303);
    exit;
}

// Hodnoty z formuláře: ořezat, omezit délku, odstranit řídicí znaky
function field(string $name, int $max, bool $oneLine = true): string {
    $v = trim((string)($_POST[$name] ?? ''));
    $v = $oneLine ? preg_replace('/[\r\n\t]+/', ' ', $v) : preg_replace('/\r\n?/', "\n", $v);
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', (string)$v);
    return mb_substr((string)$v, 0, $max);
}

// 1) Past na roboty: skryté pole musí zůstat prázdné, formulář nesmí být odeslán okamžitě
$sentAt = (int)($_POST['t'] ?? 0);
if (field('web', 200) !== '' || ($sentAt > 0 && time() - $sentAt < 3)) {
    finish(true, 'OK', $wantsJson);   // robotovi tváříme, že prošel
}

// 2) Limit na IP adresu (ukládá se jen otisk IP na 1 hodinu)
$bucket = sys_get_temp_dir() . '/poptavka_' . hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . __FILE__);
$hits = array_filter(array_map('intval', @file($bucket, FILE_IGNORE_NEW_LINES) ?: []), fn($t) => $t > time() - 3600);
if (count($hits) >= MAX_PER_HOUR) {
    finish(false, 'Odeslali jste už několik poptávek. Zkuste to prosím později, nebo zavolejte.', $wantsJson, 429);
}

// 3) Kontrola povinných polí
$d = [
    'jmeno'   => field('jmeno', 100),
    'telefon' => field('telefon', 30),
    'email'   => field('email', 120),
    'sluzba'  => field('sluzba', 60),
    'misto'   => field('misto', 100),
    'termin'  => field('termin', 100),
    'zprava'  => field('zprava', 3000, false),
];
if ($d['jmeno'] === '' || $d['telefon'] === '' || $d['misto'] === '' || $d['zprava'] === '' || empty($_POST['souhlas'])) {
    finish(false, 'Vyplňte prosím všechna povinná pole.', $wantsJson, 422);
}
if (!preg_match('/^[0-9+ ()\/-]{6,30}$/', $d['telefon'])) {
    finish(false, 'Zkontrolujte prosím telefonní číslo.', $wantsJson, 422);
}
if ($d['email'] !== '' && !filter_var($d['email'], FILTER_VALIDATE_EMAIL)) {
    finish(false, 'Zkontrolujte prosím e-mailovou adresu.', $wantsJson, 422);
}
$service = $SERVICES[$d['sluzba']] ?? 'Neuvedeno';

// 4) Sestavení e-mailu
$body = "Nová poptávka z webu " . SITE_NAME . "\n"
      . str_repeat('-', 40) . "\n"
      . "Jméno:    {$d['jmeno']}\n"
      . "Telefon:  {$d['telefon']}\n"
      . "E-mail:   " . ($d['email'] ?: '(neuvedeno)') . "\n"
      . "Služba:   {$service}\n"
      . "Místo:    {$d['misto']}\n"
      . "Termín:   " . ($d['termin'] ?: 'dle domluvy') . "\n"
      . str_repeat('-', 40) . "\n"
      . $d['zprava'] . "\n\n"
      . "Odesláno: " . date('j. n. Y H:i') . "\n"
      . "Zákazník potvrdil, že bere na vědomí zásady ochrany osobních údajů.\n";

$subject = 'Poptávka z webu: ' . $service . ' – ' . $d['misto'];
$headers = [
    'From: ' . mb_encode_mimeheader(SITE_NAME . ' – web', 'UTF-8', 'B') . ' <' . FROM_EMAIL . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: uklid-pospisil-web',
];
if ($d['email'] !== '') {
    $headers[] = 'Reply-To: =?UTF-8?B?' . base64_encode($d['jmeno']) . '?= <' . $d['email'] . '>';
}

/** Minimal SMTP client (SSL 465 nebo STARTTLS 587) s přihlášením AUTH LOGIN. */
function smtp_send(string $to, string $subject, string $body, array $headers): bool {
    $secure = defined('SMTP_SECURE') ? SMTP_SECURE : 'ssl';
    $host = ($secure === 'ssl' ? 'ssl://' : '') . SMTP_HOST;
    $fp = @stream_socket_client($host . ':' . SMTP_PORT, $errno, $errstr, 15);
    if (!$fp) { error_log("poptavka smtp connect: $errstr"); return false; }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp): string {
        $out = '';
        while (($line = fgets($fp, 515)) !== false) { $out .= $line; if (isset($line[3]) && $line[3] === ' ') break; }
        return $out;
    };
    $cmd = function (string $c, array $expect) use ($fp, $read): bool {
        if ($c !== '') fwrite($fp, $c . "\r\n");
        $r = $read();
        if (!in_array((int)substr($r, 0, 3), $expect, true)) { error_log('poptavka smtp: ' . trim($r)); return false; }
        return true;
    };
    $ehlo = 'EHLO ' . ($_SERVER['SERVER_NAME'] ?? 'localhost');
    $ok = $cmd('', [220]) && $cmd($ehlo, [250]);
    if ($ok && $secure === 'tls') {
        $ok = $cmd('STARTTLS', [220]) && stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT) && $cmd($ehlo, [250]);
    }
    $ok = $ok && $cmd('AUTH LOGIN', [334]) && $cmd(base64_encode(SMTP_USER), [334]) && $cmd(base64_encode(SMTP_PASS), [235])
        && $cmd('MAIL FROM:<' . FROM_EMAIL . '>', [250]) && $cmd('RCPT TO:<' . $to . '>', [250, 251]) && $cmd('DATA', [354]);
    if ($ok) {
        $msg = 'Date: ' . date('r') . "\r\n"
             . 'Message-ID: <' . bin2hex(random_bytes(12)) . '@' . substr(strrchr(FROM_EMAIL, '@'), 1) . ">\r\n"
             . 'To: <' . $to . ">\r\n"
             . 'Subject: ' . $subject . "\r\n"
             . implode("\r\n", str_replace('Content-Transfer-Encoding: 8bit', 'Content-Transfer-Encoding: base64', $headers)) . "\r\n\r\n"
             . chunk_split(base64_encode($body));
        $ok = $cmd($msg . "\r\n.", [250]);   // base64 body never contains a lone '.' line
    }
    @fwrite($fp, "QUIT\r\n");
    fclose($fp);
    return $ok;
}

$encSubject = mb_encode_mimeheader($subject, 'UTF-8', 'B');
if (defined('SMTP_HOST') && defined('SMTP_USER') && defined('SMTP_PASS')) {
    $ok = smtp_send(TO_EMAIL, $encSubject, $body, $headers);
} else {
    $ok = mail(TO_EMAIL, $encSubject, $body, implode("\r\n", $headers), '-f' . FROM_EMAIL);
}
if (!$ok) {
    finish(false, 'Poptávku se nepodařilo odeslat. Zavolejte nám prosím.', $wantsJson, 500);
}
$hits[] = time();
@file_put_contents($bucket, implode("\n", $hits));
finish(true, 'Děkujeme, poptávka je odeslaná.', $wantsJson);
