"""Live / simulated-live multi-stream ingestion (RTSP or real-time file replay). OWNER: P3.

Planned API:
    run(manifest_path, realtime=True)   feeds chunks into P1's per-chunk ingest and calls alerts.check_track
"""
