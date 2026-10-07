<script lang="ts">
  import ForceGraph, { type NodeObject, type LinkObject } from 'force-graph'
  import graphData from '../graph.json'

  interface GraphNode extends NodeObject {
    name: string
    type: string
  }
  type GraphLink = LinkObject<GraphNode>

  let container: HTMLDivElement

  $effect(() => {
    const graph = new ForceGraph<GraphNode, GraphLink>(container)
      .graphData({ nodes: graphData.nodes, links: graphData.links })
      .backgroundColor('#111318')
      .nodeId('id')
      .nodeAutoColorBy('type')
      .linkLabel('type')
      .linkColor(() => 'rgba(255, 255, 255, 0.3)')
      .linkDirectionalArrowLength(4)
      .nodeCanvasObjectMode(() => 'after')
      .nodeCanvasObject((node, ctx, globalScale) => {
        const fontSize = 12 / globalScale
        ctx.font = `${fontSize}px sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        ctx.fillStyle = '#eee'
        ctx.fillText(node.name, node.x ?? 0, (node.y ?? 0) + 6)
      })

    // keep the canvas sized to its container
    const resize = () =>
      graph.width(container.clientWidth).height(container.clientHeight)
    resize()
    window.addEventListener('resize', resize)

    return () => window.removeEventListener('resize', resize)
  })
</script>

<div class="graph-container" bind:this={container}></div>

<style>
  .graph-container {
    width: 100%;
    height: 100%;
    flex: 1;
    min-height: 0;
  }
</style>
