<script lang="ts">
import ForceGraph, { type LinkObject, type NodeObject } from "force-graph";
import graphData from "../graph.json";

interface GraphNode extends NodeObject {
	name: string;
	type: string;
}

interface GraphLink extends LinkObject<GraphNode>{
  type: string;
}

let container: HTMLDivElement;

// Tweak these to restyle each node type.
const nodeColors: Record<string, string> = {
	band: "#75B8C8",
	musician: "#6A66A3",
	song: "#F4E8C1",
};
const fallbackColor = "#999";

const RECT_W = 12;
const RECT_H = 8;
const RADIUS = 5;

// Draws the node's shape; used for both visible painting and the hover/click hit area.
function drawShape(
	node: GraphNode,
	color: string,
	ctx: CanvasRenderingContext2D,
) {
	const x = node.x ?? 0;
	const y = node.y ?? 0;
	ctx.fillStyle = color;
	if (node.type === "band") {
		ctx.beginPath();
		ctx.roundRect(x - RECT_W / 2, y - RECT_H / 2, RECT_W, RECT_H, 2);
    ctx.fill();
	} else if (node.type === "song") {
		ctx.beginPath();
    ctx.moveTo(x, y - 5);
    ctx.lineTo(x - 5, y + 5);
    ctx.lineTo(x + 5, y + 5);
    ctx.fill(); // triangle
	} else {
		ctx.beginPath();
		ctx.arc(x, y, RADIUS, 0, 2 * Math.PI);
		ctx.fill();
	}
}
function drawText(node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) {
	const fontSize = 12 / globalScale;
	ctx.font = `${fontSize}px sans-serif`;
	ctx.textAlign = "center";
	ctx.textBaseline = "top";
	ctx.fillStyle = "#eee";
	ctx.fillText(node.name, node.x ?? 0, (node.y ?? 0) + RADIUS + 1);
}

$effect(() => {
	const graph = new ForceGraph<GraphNode, GraphLink>(container)
		.graphData({ nodes: graphData.nodes, links: graphData.links })
		.backgroundColor("#00171F")
		.nodeId("id")
		.linkLabel("type")
    .linkLineDash(link => link.type === "guest" ? [5, 5] : [])
		.linkColor(() => "rgba(255, 255, 255, 0.3)")
		.linkDirectionalArrowLength(0)
		.nodeCanvasObject((node, ctx, globalScale) => {
			drawShape(node, nodeColors[node.type] ?? fallbackColor, ctx);
      drawText(node, ctx, globalScale);
		})
		.nodePointerAreaPaint(drawShape);

	// keep the canvas sized to its container
	const resize = () =>
		graph.width(container.clientWidth).height(container.clientHeight);
	resize();
	window.addEventListener("resize", resize);

	return () => window.removeEventListener("resize", resize);
});
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
