<script>
  import { createEventDispatcher } from 'svelte';

  /** @type {string} */
  export let value = '';
  /** @type {boolean} */
  export let loading = false;
  /** @type {boolean} */
  export let ready = false;

  const dispatch = createEventDispatcher();

  function submit() {
    if (!value.trim() || loading || !ready) return;
    dispatch('translate', value.trim());
  }
</script>

<form class="box" on:submit|preventDefault={submit}>
  <div class="box__header">
    <label class="box__eyebrow" for="source-text">Source</label>
    <span class="box__hint">Cebuano input</span>
  </div>
  <textarea
    id="source-text"
    bind:value
    placeholder="Type or choose a Cebuano example"
    rows="8"
    aria-describedby="source-help"
  ></textarea>
  <p id="source-help" class="box__help">Only the corpus examples are available in this local demo.</p>
  <button class="box__submit" type="submit" disabled={loading || !ready || !value.trim()}>
    {loading ? 'Translating…' : 'Translate to Tagalog'}
  </button>
</form>

<style>
  .box {
    display: flex;
    flex: 1 1 auto;
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(26, 34, 44, 0.92);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    min-height: 100%;
    box-sizing: border-box;
  }

  .box__header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.75rem;
  }

  .box__eyebrow {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--color-accent-teal);
  }

  .box__hint {
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }

  textarea {
    flex: 1;
    background: var(--color-surface-raised);
    color: var(--color-text);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.9rem;
    font-size: 1rem;
    line-height: 1.5;
    resize: vertical;
    min-height: 14rem;
    height: 100%;
  }

  .box__submit {
    align-self: flex-start;
    background: var(--color-accent-gold);
    color: #1a140a;
    border: none;
    border-radius: 4px;
    padding: 0.72rem 1.35rem;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: transform 0.15s ease, opacity 0.15s ease;
  }

  .box__submit:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .box__submit:not(:disabled):hover {
    background: #e2b75f;
  }

  .box__help {
    margin: -0.25rem 0 0;
    color: var(--color-text-muted);
    font-size: 0.82rem;
  }
</style>
