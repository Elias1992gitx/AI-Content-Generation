#!/usr/bin/env python3
"""
Compiles REPORT.md into a high-quality, beautifully formatted PDF report (REPORT.pdf)
using reportlab.
"""
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

BASE_DIR = Path(__file__).resolve().parent
PDF_OUTPUT_PATH = BASE_DIR / "REPORT.pdf"


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#B45309'),
        spaceAfter=8
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569')
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=4
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=7,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E3A8A'),
        leftIndent=15,
        rightIndent=15,
        spaceBefore=4,
        spaceAfter=5
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("AI-Content Generation: The Heritage Short", title_style))
    story.append(Paragraph("Technical Engineering, Design Thinking & Reflection Report", subtitle_style))
    story.append(Paragraph("<b>Project:</b> The Boy Who Grew with the Land (ከመሬቱ ጋር ያደገው ልጅ) &nbsp;|&nbsp; <b>Author:</b> Elias Chane &nbsp;|&nbsp; <b>Cohort:</b> TenX B2W0 &nbsp;|&nbsp; <b>Date:</b> November 2026", meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    # 1. Executive Summary & Intent
    story.append(Paragraph("1. Executive Summary & Intent", h1_style))
    story.append(Paragraph("<b>1.1 Project Overview:</b> 'The Boy Who Grew with the Land' is an 86-second cinematic short film documenting the childhood of my father in the rural Ethiopian highlands. Long before modern urban life, he grew up waking at dawn, herding cattle and sheep, cultivating the soil, and planting seeds. The film illustrates that character, patience, and dignity were forged through intimate responsibility to family and the land.", body_style))
    story.append(Paragraph("<i>\"Some people inherit wealth, some inherit knowledge, but my father inherited the strength of the land — and that is a legacy to be proud of.\"</i>", quote_style))
    story.append(Paragraph("<b>1.2 Target Audience & Medium:</b> Primary audience comprises family elders and the Ethiopian diaspora who cherish agricultural heritage. The production was engineered natively for mobile vertical feeds (9:16 for TikTok, Instagram Reels, Telegram) with an accompanying horizontal master (16:9 for YouTube).", body_style))

    # 2. Audience Reflection & Testing Cycles
    story.append(Paragraph("2. Audience Reflection & Testing Cycles", h1_style))
    story.append(Paragraph("<b>2.1 User Test 1: The Radio Cut (Narration & Pacing Prototype):</b> Screened an early audio-only cut to 3 target listeners. Feedback revealed vocal persona shifts between shots and abrupt transitions. In response, we strictly locked the Gemini Flash TTS persona to 'Puck' across all 8 shots and implemented 250ms natural breath pauses, ensuring a unified storytelling memory.", body_style))
    story.append(Paragraph("<b>2.2 User Test 2: Near-Final Cut (Visuals, Ducking & Subtitles):</b> Screened the vertical 9:16 export on mobile devices. Viewers noted background synthesizer buzzing behind the narration. In response, we stripped randomized noise from the ACE-Step physical synthesizer in <code>pipeline/music.py</code>, added FFT spectral denoising (<code>afftdn=nf=-25</code>) to the vocal track, lowered music gain to 0.10 (-20 dB true underscore), and re-tuned sidechain compression ducking. Background noise was completely eliminated.", body_style))

    # 3. Hardest Technical Challenge & Resolution
    story.append(Paragraph("3. Hardest Technical Challenge & Resolution", h1_style))
    story.append(Paragraph("<b>Challenge:</b> In generative media pipelines, video diffusion models typically output fixed-duration clips (e.g., 5.0 seconds). However, natural Amharic narration fluctuates between 7.5 and 14.9 seconds per shot. Early drafts cut off speech prematurely, and standard subtitle positioning was blocked by mobile UI icons (likes/comments).", body_style))
    story.append(Paragraph("<b>Resolution:</b> Built a dynamic audio-video inspection engine in <code>pipeline/shots.py</code>. The video generator probes the exact duration of the generated narration WAV for each shot and sizes the video clip to <code>AudioDuration + 0.3s</code>, perfectly synchronizing audio and visual cuts. Furthermore, subtitles were compiled into custom <code>.ass</code> scripts with a vertical bottom margin of 380 pixels (<code>MarginV=380</code>), securing text within the mobile safe-reading zone.", body_style))

    # 4. Suggested Practices Tested Honestly
    story.append(Paragraph("4. Suggested Practices Tested Honestly", h1_style))
    story.append(Paragraph("<b>4.1 Practice That Beat My Instinct (Timing Narration First via Radio Cut):</b> My initial instinct was to generate exciting video clips first. However, forcing myself to settle the radio cut first established an immutable temporal skeleton. Knowing exact shot timings in spoken Amharic prevented dozens of costly video re-renders and produced a coherent film.", body_style))
    story.append(Paragraph("<b>4.2 Practice That Did Not Beat My Instinct (Relying on Generic Text-to-Video Prompts):</b> Prompting video models directly with text descriptions without image anchors resulted in severe facial and wardrobe morphing between shots. Establishing an explicit two-step reference anchor (generating <code>character_reference.jpg</code> and <code>style_reference.jpg</code> via FLUX.1 first, and conditioning every video clip on it) drastically outperformed text-only prompting.", body_style))

    # 5. Ceiling Work & Technical Innovations
    story.append(Paragraph("5. Ceiling Work (Curiosity Beyond the Floor)", h1_style))
    story.append(Paragraph("• <b>Zero-Dependency FFmpeg Discovery:</b> Integrated an autonomous binary resolver in <code>pipeline/common.py</code> utilizing bundled <code>imageio-ffmpeg</code> Apple Silicon FFmpeg 7.1 binaries, bypassing macOS Homebrew dependencies.<br/>"
                           "• <b>Deterministic SHA-256 Incremental Caching:</b> Every stage caches assets by a 16-character SHA-256 hash. Re-running <code>make film</code> executes in <b>12.7 seconds</b> with 100% cache hits, enabling rapid 1-shot live regeneration demos.<br/>"
                           "• <b>Physical Instrument Synthesis in Ethiopian Pentatonic Modes:</b> Synthesized authentic washint flute vibrato, plucked krar lyre, and nylon guitar in Ethiopian Tizita Minor, Bati Major, and Anchihoye modes.", body_style))

    # 6. Future Roadmap
    story.append(Paragraph("6. Future Roadmap", h1_style))
    story.append(Paragraph("• <b>Multilingual Expansion:</b> Extend <code>pipeline/narration.py</code> to support automated prosody-matched dubbing in Afaan Oromo, Tigrinya, and Somali.<br/>"
                           "• <b>Family Archival Web Studio:</b> Wrap the CLI studio into an accessible Web/Gradio interface allowing family members to upload voice notes and automatically generate heritage films.", body_style))

    # 7. Verification & Deliverables Table
    story.append(Spacer(1, 4))
    story.append(Paragraph("7. Verified Deliverables & Repository Map", h1_style))

    table_data = [
        [Paragraph("Deliverable", table_cell_bold), Paragraph("Repository Path / Asset", table_cell_bold), Paragraph("Verification Details", table_cell_bold)],
        [Paragraph("<b>One-Command Run</b>", table_cell), Paragraph("<code>Makefile</code> (<code>make film</code>)", table_cell), Paragraph("Validated end-to-end; 12.7s cached pass", table_cell)],
        [Paragraph("<b>Vertical Master (9:16)</b>", table_cell), Paragraph("<code>outputs/final/short_vertical_9_16.mp4</code>", table_cell), Paragraph("1080x1920 • 86.3s • -16 LUFS • Burned English Subs", table_cell)],
        [Paragraph("<b>Horizontal Master (16:9)</b>", table_cell), Paragraph("<code>outputs/final/short_horizontal_16_9.mp4</code>", table_cell), Paragraph("1920x1080 • 86.3s • -16 LUFS • Burned English Subs", table_cell)],
        [Paragraph("<b>Storyboard Contract</b>", table_cell), Paragraph("<code>storyboard.json</code> & <code>schema/</code>", table_cell), Paragraph("Draft-07 schema validated; 8 narrative shots", table_cell)],
        [Paragraph("<b>Telemetry Log</b>", table_cell), Paragraph("<code>runs.jsonl</code>", table_cell), Paragraph("Audit log of latency, parameters, seeds & cost ($0.00)", table_cell)],
        [Paragraph("<b>Experiments Log</b>", table_cell), Paragraph("<code>EXPERIMENTS.md</code>", table_cell), Paragraph("11 hypothesis-driven entries documented", table_cell)],
        [Paragraph("<b>Post-Mortem Journal</b>", table_cell), Paragraph("<code>FAILURES.md</code>", table_cell), Paragraph("5 technical blocker post-mortems documented", table_cell)],
        [Paragraph("<b>Ethics & Consent</b>", table_cell), Paragraph("<code>ETHICS.md</code>", table_cell), Paragraph("Family informed consent & Apache 2.0/MIT licenses", table_cell)]
    ]

    t = Table(table_data, colWidths=[120, 210, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)

    doc.build(story)
    print(f"✅ Generated PDF report: {PDF_OUTPUT_PATH} ({PDF_OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build_pdf()

