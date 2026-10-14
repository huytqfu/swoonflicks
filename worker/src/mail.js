// Nội dung email gửi mã mời, 3 ngôn ngữ (khớp trang /invite/rs-boost/, /es/, /pt/).
// Khung theo mail Drama Partner sếp gửi 14/10 21:03: tiêu đề "code is ready" → khối mã → nút đăng ký chính thức →
// "Before you register" 4 lưu ý an toàn → link guide → chân "transactional email". Bản EN–VI để duyệt: docs/invite-email-gate/email-copy.md.
// Logo: lockup thật của site (brand v3c) qua URL công khai, không chế logo mới.

const LOGO = "https://swoonflicks.com/img/lockup-sm.png";  // 354x52, không tagline
const SITE = "https://swoonflicks.com";

const T = {
  en: {
    subject: (p) => `Your ${p} invite code is ready`,
    preheader: "The code you requested, the official registration link and 4 things to check before you register.",
    intro: (p) => `Thanks for requesting a ReelShort ${p} invite code from Swoonflicks. We send it personally, on request. Copy the code below, then complete your account on the official registration page.`,
    codeLabel: (p) => `ReelShort ${p} invite code`,
    cta: "Open the official ReelShort registration page",
    beforeH: "Before you register",
    before: [
      "Make sure the page is on the official cps.reelshort.com domain.",
      "Enter your email, verification code and password as requested.",
      "Paste the invite code above and check every character before submitting.",
      "Never share your password or email verification code with anyone."
    ],
    warn: "A bound invite code may not be changeable later, so paste it during sign-up.",
    guide: (u) => `For screenshots, step-by-step help and common questions, read the <a href="${u}" style="color:#f4406d;font-weight:700">registration guide</a>.`,
    guideText: (u) => `Step-by-step guide: ${u}`,
    help: "Stuck somewhere? Reply to this email and a real person at Swoonflicks will answer.",
    disclosure: (p) => `This is our referral code. If you join ${p} with it, ReelShort may give us a better commission rate. It costs you nothing and does not change what you earn.`,
    footer: (page) => `You received this transactional email because someone entered this address at ${page} to request an invite code. This request does not subscribe you to anything: one email, no newsletter.`,
    guidePath: "/guides/how-to-join-rs-boost/"
  },
  es: {
    subject: (p) => `Tu código de invitación de ${p} está listo`,
    preheader: "El código que pediste, el enlace oficial de registro y 4 cosas que revisar antes de registrarte.",
    intro: (p) => `Gracias por pedir un código de invitación de ReelShort ${p} a Swoonflicks. Lo enviamos personalmente, a petición. Copia el código de abajo y completa tu cuenta en la página oficial de registro.`,
    codeLabel: (p) => `Código de invitación ReelShort ${p}`,
    cta: "Abrir la página oficial de registro de ReelShort",
    beforeH: "Antes de registrarte",
    before: [
      "Comprueba que la página esté en el dominio oficial cps.reelshort.com.",
      "Introduce tu correo, el código de verificación y la contraseña que te pidan.",
      "Pega el código de invitación de arriba y revisa cada carácter antes de enviar.",
      "Nunca compartas tu contraseña ni el código de verificación del correo con nadie."
    ],
    warn: "Puede que el código vinculado no se pueda cambiar después, así que pégalo durante el registro.",
    guide: (u) => `Para capturas, ayuda paso a paso y preguntas frecuentes, lee la <a href="${u}" style="color:#f4406d;font-weight:700">guía de registro</a>.`,
    guideText: (u) => `Guía paso a paso: ${u}`,
    help: "¿Te atascaste? Responde a este correo y una persona real de Swoonflicks te contesta.",
    disclosure: (p) => `Este es nuestro código de referido. Si te registras en ${p} con él, ReelShort puede darnos una mejor comisión. A ti no te cuesta nada y no cambia lo que ganas.`,
    footer: (page) => `Recibes este correo transaccional porque alguien escribió esta dirección en ${page} para pedir un código de invitación. No te suscribe a nada: un solo correo, sin boletín.`,
    guidePath: "/es/invite/rs-boost/"
  },
  pt: {
    subject: (p) => `Seu código de convite do ${p} está pronto`,
    preheader: "O código que você pediu, o link oficial de cadastro e 4 coisas para conferir antes de se cadastrar.",
    intro: (p) => `Obrigado por pedir um código de convite do ReelShort ${p} à Swoonflicks. Enviamos pessoalmente, a pedido. Copie o código abaixo e conclua sua conta na página oficial de cadastro.`,
    codeLabel: (p) => `Código de convite ReelShort ${p}`,
    cta: "Abrir a página oficial de cadastro da ReelShort",
    beforeH: "Antes de se cadastrar",
    before: [
      "Confira se a página está no domínio oficial cps.reelshort.com.",
      "Informe seu e-mail, o código de verificação e a senha pedidos.",
      "Cole o código de convite acima e confira cada caractere antes de enviar.",
      "Nunca compartilhe sua senha nem o código de verificação do e-mail com ninguém."
    ],
    warn: "O código vinculado talvez não possa ser trocado depois, então cole durante o cadastro.",
    guide: (u) => `Para capturas de tela, ajuda passo a passo e dúvidas comuns, leia o <a href="${u}" style="color:#f4406d;font-weight:700">guia de cadastro</a>.`,
    guideText: (u) => `Guia passo a passo: ${u}`,
    help: "Travou em algum passo? Responda a este e-mail e uma pessoa de verdade da Swoonflicks responde.",
    disclosure: (p) => `Este é o nosso código de indicação. Se você se cadastrar no ${p} com ele, a ReelShort pode nos dar uma comissão melhor. Para você não custa nada e não muda o que você ganha.`,
    footer: (page) => `Você recebeu este e-mail transacional porque alguém informou este endereço em ${page} para pedir um código de convite. Isso não assina nada: um único e-mail, sem newsletter.`,
    guidePath: "/pt/invite/rs-boost/"
  }
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function buildMail({ lang, program, code, signup, page }) {
  const t = T[lang] || T.en;
  const pageUrl = SITE + (page || "/invite/");
  const guideUrl = SITE + t.guidePath;
  const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(t.subject(program))}</title></head>
<body style="margin:0;padding:0;background:#0b0709;font-family:Poppins,Helvetica,Arial,sans-serif;color:#f6f4f7">
<span style="display:none;max-height:0;overflow:hidden;color:#0b0709">${esc(t.preheader)}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0b0709"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#171015;border-radius:16px;overflow:hidden;border-top:4px solid #f4406d">
<tr><td style="padding:24px 24px 0"><a href="${SITE}/"><img src="${LOGO}" alt="Swoonflicks" width="150" style="display:block;width:150px;height:auto;border:0"></a></td></tr>
<tr><td style="padding:18px 24px 8px;font-size:16px;line-height:1.55">
<h1 style="margin:0 0 14px;font-size:28px;line-height:1.2;color:#ffffff">${esc(t.subject(program))}</h1>
<p style="margin:0 0 20px;color:#e2d6dc">${esc(t.intro(program))}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="background:#0b0709;border:1px solid #740827;border-radius:14px;padding:18px 20px" align="center">
<div style="font:700 12px/1 Helvetica,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#ff8fab">${esc(t.codeLabel(program))}</div>
<div style="margin-top:10px;font:800 30px/1.1 Consolas,Menlo,monospace;letter-spacing:.08em;color:#ffffff">${esc(code)}</div>
</td></tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:18px"><tr><td style="background:#f4406d;border-radius:999px" align="center">
<a href="${esc(signup)}" style="display:block;padding:16px 22px;font:700 17px/1.25 Poppins,Helvetica,Arial,sans-serif;color:#ffffff;text-decoration:none">${esc(t.cta)}</a></td></tr></table>
<h2 style="margin:26px 0 8px;font-size:18px;color:#ffffff">${esc(t.beforeH)}</h2>
<ol style="margin:0;padding-left:22px;color:#e2d6dc">${t.before.map((s) => `<li style="margin:0 0 8px">${esc(s)}</li>`).join("")}</ol>
<p style="margin:12px 0 0;font-size:13px;color:#b5a3ad">${esc(t.warn)}</p>
<p style="margin:18px 0 0;color:#e2d6dc">${t.guide(guideUrl)}</p>
<p style="margin:16px 0 0;font-size:14px;color:#e2d6dc">${esc(t.help)}</p>
</td></tr>
<tr><td style="padding:16px 24px 26px;font-size:12px;line-height:1.6;color:#b5a3ad;border-top:1px solid #34202b">
<p style="margin:0 0 8px">${esc(t.disclosure(program))}</p>
<p style="margin:0">${esc(t.footer(pageUrl))} · <a href="${SITE}/privacy/" style="color:#b5a3ad">Privacy</a></p>
</td></tr></table></td></tr></table></body></html>`;
  const text = [
    t.subject(program), "", t.intro(program), "", `${t.codeLabel(program)}: ${code}`, "", `${t.cta}: ${signup}`, "", `${t.beforeH}:`,
    ...t.before.map((s, i) => `${i + 1}. ${s}`), t.warn, "", t.guideText(guideUrl), "", t.help, "", t.disclosure(program), t.footer(pageUrl), `${SITE}/privacy/`
  ].join("\n");
  return { subject: t.subject(program), html, text };
}
