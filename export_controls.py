# export_controls.py

from dash import html, dcc, Output, Input, State, ctx, callback_context, no_update
import dash_bootstrap_components as dbc
import plotly.io as pio
import pandas as pd
import io
import base64


def get_export_controls():
    return html.Div([
        html.Label("Export diagram/data", className="fw-bold mb-2"),

        html.Div([
            dcc.Dropdown(
                id="export-type",
                options=[
                    {"label": "Diagram", "value": "diagram"},
                    {"label": "Data", "value": "data"},
                ],
                placeholder="Diagram or Data",
                value="diagram",
                style={"maxWidth": "160px"},
                className="me-2"
            ),

            dcc.Dropdown(
                id="export-format",
                placeholder="Choose export type",
                style={"maxWidth": "160px"},
                className="me-3"
            ),

            html.Button("EXPORT", id="export-btn", n_clicks=0,
                        style={"border": "1px solid black", "fontWeight": "bold", "height": "38px", "padding": "0 15px"})
        ], className="d-flex align-items-center mb-4"),

        dcc.Download(id="export-download")
    ], style={"paddingLeft": "15px"})


def register_export_callbacks(app, data_getter, fig_getter):

    @app.callback(
        Output("export-format", "options"),
        Output("export-format", "value"),
        Input("export-type", "value")
    )
    def update_format_options(export_type):
        if export_type == "diagram":
            return [
                {"label": "PNG", "value": "png"},
                {"label": "JPEG", "value": "jpeg"},
                {"label": "SVG", "value": "svg"},
                {"label": "PDF", "value": "pdf"},
            ], "png"
        elif export_type == "data":
            return [
                {"label": "CSV", "value": "csv"},
                {"label": "XLS", "value": "xls"},
                {"label": "PDF", "value": "pdf"},
            ], "csv"
        return [], None

    @app.callback(
        Output("export-download", "data"),
        Input("export-btn", "n_clicks"),
        State("export-type", "value"),
        State("export-format", "value"),
        prevent_initial_call=True
    )
    def trigger_export(n_clicks, export_type, export_format):
        if export_type == "data":
            df = data_getter()
            if df.empty:
                return no_update

            if export_format == "csv":
                return dcc.send_data_frame(df.to_csv, filename="export.csv", index=False)
            elif export_format == "xls":
                return dcc.send_data_frame(df.to_excel, filename="export.xlsx", index=False, sheet_name="Sheet1")
            elif export_format == "pdf":
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter

                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                data = [df.columns.tolist()] + df.values.tolist()
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                doc.build([table])
                buffer.seek(0)
                return dict(content=buffer.read(), filename="export.pdf", base64=False, type="application/pdf")

        elif export_type == "diagram":
            fig = fig_getter()
            img_bytes = fig.to_image(format=export_format)
            encoded = base64.b64encode(img_bytes).decode()
            mime = f"image/{export_format if export_format != 'svg' else 'svg+xml'}"
            return dict(content=img_bytes, filename=f"chart.{export_format}", base64=False, type=mime)

        return no_update
