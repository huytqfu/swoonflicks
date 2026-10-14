// Nội dung email gửi mã mời, 3 ngôn ngữ (khớp trang /invite/rs-boost/, /es/, /pt/).
// Chữ bản EN–VI để sếp duyệt nằm ở docs/invite-email-gate/email-copy.md; đổi chữ ở đó rồi chép vào đây.
// Logo: dùng lockup thật của site (brand v3c) qua URL công khai, không chế logo mới.

const LOGO = "https://swoonflicks.com/img/lockup-sm.png";  // 354x52, không tagline
const SITE = "https://swoonflicks.com";

const T = {
  en: {
    subject: (p) => `Your personal ${p} invite code (sent on request)`,
    preheader: "Here is the code you asked for, with the sign-up link and a 4-step checklist.",
    hi: "Hi there,",
    intro: (p) => `You asked for our ${p} invite code, so here it is. We share it personally, by request, with people who are actually signing up.`,
    codeLabel: (p) => `Your ${p} invitation code`,
    keep: "Keep it handy: you will need it once, during sign-up.",
    stepsH: "How to use it",
    steps: (p) => [
      `Open the ${p} sign-up page and choose to register.`,
      "Fill in the account details the form asks for.",
      "Paste the code above into the invitation code field.",
      "Finish sign-up, log in and set up your promotion links."
    ],
    warn: "Treat the code as permanent: it may not be possible to change it after sign-up.",
    cta: (p) => `Open ${p} sign-up`,
    help: "Stuck somewhere? Reply to this email and a real person at Swoonflicks will answer.",
    disclosure: (p) => `This is our referral code. If you join ${p} with it, ReelShort may give us a better commission rate. It costs you nothing and does not change what you earn.`,
    footer: (page) => `You received this one email because you requested the code at ${page}. No newsletter, no follow-ups.`,
    plainSteps: "Steps"
  },
  es: {
    subject: (p) => `Tu código de invitación personal de ${p} (enviado a petición)`,
    preheader: "Aquí está el código que pediste, con el enlace de registro y 4 pasos.",
    hi: "Hola,",
    intro: (p) => `Pediste nuestro código de invitación de ${p}; aquí lo tienes. Lo compartimos personalmente, a petición, con quien de verdad se va a registrar.`,
    codeLabel: (p) => `Tu código de invitación de ${p}`,
    keep: "Guárdalo a mano: lo necesitarás una sola vez, durante el registro.",
    stepsH: "Cómo usarlo",
    steps: (p) => [
      `Abre la página de registro de ${p}.`,
      "Completa los datos de la cuenta que pide el formulario.",
      "Pega el código de arriba en la casilla del código de invitación.",
      "Termina el registro, inicia sesión y crea tus enlaces de promoción."
    ],
    warn: "Considera el código como permanente: puede que no se pueda cambiar después del registro.",
    cta: (p) => `Abrir el registro de ${p}`,
    help: "¿Te atascaste? Responde a este correo y una persona real de Swoonflicks te contesta.",
    disclosure: (p) => `Este es nuestro código de referido. Si te registras en ${p} con él, ReelShort puede darnos una mejor comisión. A ti no te cuesta nada y no cambia lo que ganas.`,
    footer: (page) => `Recibes este único correo porque pediste el código en ${page}. Sin boletín ni seguimientos.`,
    plainSteps: "Pasos"
  },
  pt: {
    subject: (p) => `Seu código de convite pessoal do ${p} (enviado a pedido)`,
    preheader: "Aqui está o código que você pediu, com o link de cadastro e 4 passos.",
    hi: "Olá,",
    intro: (p) => `Você pediu nosso código de convite do ${p}; aqui está. Compartilhamos pessoalmente, a pedido, com quem vai mesmo se cadastrar.`,
    codeLabel: (p) => `Seu código de convite do ${p}`,
    keep: "Deixe à mão: você vai precisar dele uma vez, durante o cadastro.",
    stepsH: "Como usar",
    steps: (p) => [
      `Abra a página de cadastro do ${p}.`,
      "Preencha os dados da conta que o formulário pede.",
      "Cole o código acima no campo do código de convite.",
      "Conclua o cadastro, entre e crie seus links de promoção."
    ],
    warn: "Considere o código permanente: talvez não seja possível trocá-lo depois do cadastro.",
    cta: (p) => `Abrir o cadastro do ${p}`,
    help: "Travou em algum passo? Responda a este e-mail e uma pessoa de verdade da Swoonflicks responde.",
    disclosure: (p) => `Este é o nosso código de indicação. Se você se cadastrar no ${p} com ele, a ReelShort pode nos dar uma comissão melhor. Para você não custa nada e não muda o que você ganha.`,
    footer: (page) => `Você recebeu este único e-mail porque pediu o código em ${page}. Sem newsletter, sem cobranças.`,
    plainSteps: "Passos"
  }
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function buildMail({ lang, program, code, signup, page }) {
  const t = T[lang] || T.en;
  const pageUrl = SITE + (page || "/invite/");
  const steps = t.steps(program);
  const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(t.subject(program))}</title></head>
<body style="margin:0;padding:0;background:#f6f4f7;font-family:Poppins,Helvetica,Arial,sans-serif;color:#1a1216">
<span style="display:none;max-height:0;overflow:hidden;color:#f6f4f7">${esc(t.preheader)}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f4f7"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden">
<tr><td style="background:#0b0709;padding:22px 24px" align="center"><a href="${SITE}/"><img src="${LOGO}" alt="Swoonflicks" width="177" style="display:block;width:177px;height:auto;border:0"></a></td></tr>
<tr><td style="padding:28px 24px 8px;font-size:16px;line-height:1.55">
<p style="margin:0 0 12px">${esc(t.hi)}</p>
<p style="margin:0 0 20px">${esc(t.intro(program))}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="background:#0b0709;border-radius:14px;padding:18px 20px" align="center">
<div style="font:700 11px/1 Helvetica,Arial,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#ff8fab">${esc(t.codeLabel(program))}</div>
<div style="margin-top:10px;font:800 28px/1.1 Consolas,Menlo,monospace;letter-spacing:.1em;color:#ffffff">${esc(code)}</div>
</td></tr></table>
<p style="margin:12px 0 0;font-size:13px;color:#6b5a63">${esc(t.keep)}</p>
<h2 style="margin:26px 0 8px;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:#f4406d">${esc(t.stepsH)}</h2>
<ol style="margin:0;padding-left:22px">${steps.map((s) => `<li style="margin:0 0 8px">${esc(s)}</li>`).join("")}</ol>
<p style="margin:12px 0 0;font-size:13px;color:#6b5a63">${esc(t.warn)}</p>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:22px auto 0"><tr><td style="background:#f4406d;border-radius:12px" align="center">
<a href="${esc(signup)}" style="display:inline-block;padding:14px 26px;font:700 16px Poppins,Helvetica,Arial,sans-serif;color:#ffffff;text-decoration:none">${esc(t.cta(program))}</a></td></tr></table>
<p style="margin:22px 0 0;font-size:14px">${esc(t.help)}</p>
</td></tr>
<tr><td style="padding:16px 24px 26px;font-size:12px;line-height:1.6;color:#8a7a82;border-top:1px solid #eee3e8">
<p style="margin:0 0 8px">${esc(t.disclosure(program))}</p>
<p style="margin:0">${esc(t.footer(pageUrl))} · <a href="${SITE}/privacy/" style="color:#8a7a82">Privacy</a></p>
</td></tr></table></td></tr></table></body></html>`;
  const text = [
    t.hi, "", t.intro(program), "", `${t.codeLabel(program)}: ${code}`, t.keep, "", `${t.plainSteps}:`,
    ...steps.map((s, i) => `${i + 1}. ${s}`), t.warn, "", `${t.cta(program)}: ${signup}`, "", t.help, "", t.disclosure(program), t.footer(pageUrl), `${SITE}/privacy/`
  ].join("\n");
  return { subject: t.subject(program), html, text };
}
