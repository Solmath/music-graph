<script lang="ts">
import GraphView from "./GraphView.svelte";
</script>

<div class="page">
  <h1>Band Graph</h1>
  <GraphView />
</div>

<style>
  :global(html),
  :global(body) {
    margin: 0;
    height: 100%;
    background: #111318;
    color: #eee;
    color-scheme: dark;
  }

  .page {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  h1 {
    margin: 0;
    padding: 0.5rem 1rem;
    flex: none;
  }
</style>
