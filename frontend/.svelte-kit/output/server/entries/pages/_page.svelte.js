import { a7 as fallback, e as escape_html, a8 as ensure_array_like, a9 as bind_props, aa as attr, ab as head } from "../../chunks/index.js";
const DEMO_CORPUS = [
  { source_text: "Maayong buntag.", target_text: "Magandang umaga." },
  { source_text: "Asa ka paingon?", target_text: "Saan ka pupunta?" },
  { source_text: "Palihog tabangi ko.", target_text: "Pakiusap, tulungan mo ako." },
  { source_text: "Dako kaayo ang kalipay nako.", target_text: "Napakasaya ko ngayon." },
  { source_text: "Unsa imong ngalan?", target_text: "Ano ang iyong pangalan?" },
  { source_text: "Mao ra ni ang akong gusto.", target_text: "Iyan lang ang gusto ko." }
];
new Map(
  DEMO_CORPUS.map(({ source_text, target_text }) => [source_text.trim().toLowerCase(), target_text])
);
function ModelPicker($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let selectedModel;
    let models = fallback($$props["models"], () => [], true);
    let selected = fallback($$props["selected"], "");
    selectedModel = models.find((model) => model.name === selected) ?? null;
    $$renderer2.push(`<section class="picker svelte-zkyht3" aria-labelledby="model-heading"><div class="picker__header svelte-zkyht3"><div><span class="picker__label svelte-zkyht3">Modelo</span> <h2 id="model-heading" class="svelte-zkyht3">Translation model</h2></div> `);
    if (selectedModel) {
      $$renderer2.push(`<!--[0--><div class="picker__summary svelte-zkyht3">`);
      if (selectedModel.bidirectional) {
        $$renderer2.push(`<!--[0--><span class="svelte-zkyht3">Bidirectional</span>`);
      } else {
        $$renderer2.push("<!--[-1-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (selectedModel.peeky) {
        $$renderer2.push(`<!--[0--><span class="svelte-zkyht3">Peeky decoder</span>`);
      } else {
        $$renderer2.push("<!--[-1-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (selectedModel.bleu != null) {
        $$renderer2.push(`<!--[0--><span class="svelte-zkyht3">BLEU ${escape_html(selectedModel.bleu.toFixed(1))}</span>`);
      } else {
        $$renderer2.push("<!--[-1-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    $$renderer2.select(
      {
        value: selected,
        class: "picker__select",
        "aria-label": "Select translation model"
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(models);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let model = each_array[$$index];
          $$renderer3.option({ value: model.name }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(model.name)}${escape_html(model.bleu != null ? ` · BLEU ${model.bleu.toFixed(1)}` : "")}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      },
      "svelte-zkyht3"
    );
    $$renderer2.push(` `);
    if (selectedModel) {
      $$renderer2.push(`<!--[0--><p class="picker__details svelte-zkyht3">${escape_html(selectedModel.name)} is the active run for Cebuano to Tagalog translation.</p>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></section>`);
    bind_props($$props, { models, selected });
  });
}
function TranslateBox($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let value = fallback($$props["value"], "");
    let loading = fallback($$props["loading"], false);
    let ready = fallback($$props["ready"], false);
    $$renderer2.push(`<form class="box svelte-r43oqp"><div class="box__header svelte-r43oqp"><label class="box__eyebrow svelte-r43oqp" for="source-text">Source</label> <span class="box__hint svelte-r43oqp">Cebuano input</span></div> <textarea id="source-text" placeholder="Type or choose a Cebuano example" rows="8" aria-describedby="source-help" class="svelte-r43oqp">`);
    const $$body = escape_html(value);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea> <p id="source-help" class="box__help svelte-r43oqp">Only the corpus examples are available in this local demo.</p> <button class="box__submit svelte-r43oqp" type="submit"${attr("disabled", loading || !ready || !value.trim(), true)}>${escape_html(loading ? "Translating…" : "Translate to Tagalog")}</button></form>`);
    bind_props($$props, { value, loading, ready });
  });
}
function ResultCard($$renderer, $$props) {
  let text = fallback($$props["text"], "");
  let loading = fallback($$props["loading"], false);
  let error = fallback($$props["error"], "");
  $$renderer.push(`<section class="result svelte-1r7q0ep" aria-labelledby="result-heading"><div class="result__header svelte-1r7q0ep"><span id="result-heading" class="result__eyebrow svelte-1r7q0ep">Target</span> <span class="result__hint svelte-1r7q0ep">Tagalog output</span></div> <div class="result__body svelte-1r7q0ep" aria-live="polite">`);
  if (loading) {
    $$renderer.push(`<!--[0--><p class="result__status svelte-1r7q0ep">Running translation...</p>`);
  } else if (error) {
    $$renderer.push(`<!--[1--><p class="result__error svelte-1r7q0ep">${escape_html(error)}</p>`);
  } else if (text) {
    $$renderer.push(`<!--[2--><p>${escape_html(text)}</p>`);
  } else {
    $$renderer.push(`<!--[-1--><p class="result__status svelte-1r7q0ep">Your translation will appear here.</p>`);
  }
  $$renderer.push(`<!--]--></div></section>`);
  bind_props($$props, { text, loading, error });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let canTranslate;
    let models = [];
    let selectedModel = "";
    let inputText = "";
    let outputText = "";
    let loading = false;
    let error = "";
    let samples = ["Maayong buntag.", "Asa ka paingon?", "Palihog tabangi ko."];
    let corpusMessage = "Loading local demo corpus...";
    canTranslate = models.length > 0 && !!selectedModel;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      head("1uha8ag", $$renderer3, ($$renderer4) => {
        $$renderer4.title(($$renderer5) => {
          $$renderer5.push(`<title>SalinWika | Cebuano to Tagalog</title>`);
        });
        $$renderer4.push(`<meta name="description" content="SalinWika is a local interface for Cebuano to Tagalog translation demos."/>`);
      });
      $$renderer3.push(`<main class="page svelte-1uha8ag"><header class="masthead svelte-1uha8ag"><div><p class="masthead__brand svelte-1uha8ag">SalinWika</p> <h1 class="svelte-1uha8ag">Cebuano to Tagalog</h1></div> <p class="masthead__description svelte-1uha8ag">A local translation demo built from the project corpus.</p></header> <section class="examples svelte-1uha8ag" aria-labelledby="examples-heading"><div class="examples__heading svelte-1uha8ag"><div><p class="examples__label svelte-1uha8ag">Corpus examples</p> <h2 id="examples-heading" class="svelte-1uha8ag">Choose text to translate</h2></div> <p class="examples__message svelte-1uha8ag">${escape_html(corpusMessage)}</p></div> <div class="examples__buttons svelte-1uha8ag"><!--[-->`);
      const each_array = ensure_array_like(samples);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let sample = each_array[$$index];
        $$renderer3.push(`<button class="examples__button svelte-1uha8ag" type="button">${escape_html(sample)}</button>`);
      }
      $$renderer3.push(`<!--]--></div></section> `);
      {
        $$renderer3.push("<!--[-1-->");
      }
      $$renderer3.push(`<!--]--> `);
      if (models.length) {
        $$renderer3.push(`<!--[0--><div class="page__model svelte-1uha8ag">`);
        ModelPicker($$renderer3, {
          models,
          get selected() {
            return selectedModel;
          },
          set selected($$value) {
            selectedModel = $$value;
            $$settled = false;
          }
        });
        $$renderer3.push(`<!----></div>`);
      } else {
        $$renderer3.push(`<!--[-1--><p class="page__status svelte-1uha8ag">No local demo model is available yet.</p>`);
      }
      $$renderer3.push(`<!--]--> <section class="panels svelte-1uha8ag">`);
      TranslateBox($$renderer3, {
        loading,
        ready: canTranslate,
        get value() {
          return inputText;
        },
        set value($$value) {
          inputText = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----> <div class="panels__divider svelte-1uha8ag" aria-hidden="true"></div> `);
      ResultCard($$renderer3, { text: outputText, loading, error });
      $$renderer3.push(`<!----></section></main>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};
