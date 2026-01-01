import os
import statistics
from pathlib import Path
from zipfile import ZipFile

import fitz  # PyMuPDF
import typer
from rich.progress import BarColumn, Progress, TextColumn

app = typer.Typer(help="PDF から CBZ 形式へ変換するツール")

data_path = Path("/data")


@app.command()
def convert(
    pdf_name: str = typer.Argument(..., help="変換対象の PDF ファイルパス"),
    height_px: int | None = typer.Option(
        None,
        "--height",
        "-h",
        help="画像の高さ（ピクセル）。指定しない場合はオリジナルサイズを使用",
    ),
    limit: int | None = typer.Option(
        None,
        "--limit",
        "-l",
        help="最初の N ページだけを変換。指定しない場合は全ページを変換",
    ),
) -> None:
    """PDF ファイルを CBZ 形式に変換します"""

    pdf_path = data_path / pdf_name
    tmp_path = pdf_path.with_suffix("")
    if not tmp_path.exists():
        os.makedirs(tmp_path)

    with fitz.open(pdf_path) as doc:
        num_pages = len(doc) if limit is None else min(limit, len(doc))
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[cyan]{task.completed}/{task.total}"),
        ) as progress:
            task = progress.add_task("Converting pages...", total=num_pages)
            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                rect = page.rect
                scale = 1.0 if height_px is None else height_px / rect.height
                matrix = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=matrix)
                pix.save(f"{tmp_path}/{page_num + 1:03d}.jpg")
                progress.advance(task)

    # ZIP に圧縮
    zip_path = pdf_path.with_suffix(".zip")
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[cyan]{task.completed}/{task.total}"),
    ) as progress:
        files = sorted(tmp_path.glob("*.jpg"))
        task = progress.add_task("Creating CBZ...", total=len(files))
        with ZipFile(zip_path, "w") as zipf:
            for file in files:
                zipf.write(file, arcname=file.name)
                progress.advance(task)

    # CBZ にリネーム
    cbz_path = pdf_path.with_suffix(".cbz")
    os.rename(zip_path, cbz_path)

    # 一時ディレクトリを削除
    for file in tmp_path.glob("*"):
        os.remove(file)
    os.rmdir(tmp_path)

    typer.echo(f"✓ Completed: {cbz_path}")


@app.command()
def inspect(pdf_path: str = typer.Argument(..., help="検査対象の PDF ファイルパス")) -> None:
    """PDF ファイルのメタデータと仕様を表示します"""

    with fitz.open(pdf_path) as doc:
        # メタデータの取得
        metadata = doc.metadata
        page_count = len(doc)

        # ページのサイズを取得
        widths = []
        heights = []
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            rect = page.rect
            widths.append(rect.width)
            heights.append(rect.height)

        # ページ数が 10 以上の場合は外れ値を除外
        if page_count >= 10:
            widths_filtered = _filter_outliers(widths)
            heights_filtered = _filter_outliers(heights)
        else:
            widths_filtered = widths
            heights_filtered = heights

        avg_width = sum(widths_filtered) / len(widths_filtered)
        avg_height = sum(heights_filtered) / len(heights_filtered)

        # 結果の表示
        typer.echo("\n" + "=" * 50)
        typer.echo(f"PDF Inspection: {pdf_path}")
        typer.echo("=" * 50)

        # メタデータの表示
        if metadata:
            typer.echo("\n📄 Metadata:")
            if metadata.get("title"):
                typer.echo(f"  Title: {metadata['title']}")
            if metadata.get("author"):
                typer.echo(f"  Author: {metadata['author']}")
            if metadata.get("subject"):
                typer.echo(f"  Subject: {metadata['subject']}")
            if metadata.get("creator"):
                typer.echo(f"  Creator: {metadata['creator']}")
            if metadata.get("producer"):
                typer.echo(f"  Producer: {metadata['producer']}")
        else:
            typer.echo("\n📄 Metadata: None found")

        # ページ情報の表示
        typer.echo(f"\n📖 Pages: {page_count}")
        typer.echo("📏 Size:")
        typer.echo(f"  Width: {avg_width:.2f}")
        typer.echo(f"  Height: {avg_height:.2f}")
        typer.echo("=" * 50 + "\n")


def _filter_outliers(data: list[float]) -> list[float]:
    """四分位数法（IQR）を使用して外れ値を除外"""
    if len(data) < 4:
        return data

    sorted_data = sorted(data)
    q1 = statistics.quantiles(sorted_data, n=4)[0]
    q3 = statistics.quantiles(sorted_data, n=4)[2]
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return [x for x in data if lower_bound <= x <= upper_bound]


if __name__ == "__main__":
    app()
