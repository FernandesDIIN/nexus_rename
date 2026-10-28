import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from core.alignment import AlignmentModel
from core.batch_generator import generate_batch_mapping
from core.renamer import execute_rename, execute_rollback
from utils.file_handler import get_valid_images
from utils.logger import create_rollback_log
from ui.preview_window import load_thumbnail


class RenameTests(unittest.TestCase):
    def test_cycle_is_renamed_without_suffixes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first, second = root / "1.jpg", root / "2.jpg"
            first.write_bytes(b"first")
            second.write_bytes(b"second")

            results, pairs = execute_rename([(str(first), str(second)), (str(second), str(first))])

            self.assertEqual(results["errors"], [])
            self.assertEqual(results["success"], 2)
            self.assertEqual(first.read_bytes(), b"second")
            self.assertEqual(second.read_bytes(), b"first")
            self.assertEqual(len(pairs), 2)

    def test_external_collision_gets_a_suffix(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, occupied = root / "source.jpg", root / "name.jpg"
            source.write_bytes(b"new")
            occupied.write_bytes(b"old")

            results, pairs = execute_rename([(str(source), str(occupied))])

            self.assertEqual(results["success"], 1)
            self.assertEqual(occupied.read_bytes(), b"old")
            self.assertEqual(Path(pairs[0][1]).name, "name_1.jpg")

    def test_rollback_restores_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, target = root / "before.jpg", root / "after.jpg"
            source.write_bytes(b"image")
            _, pairs = execute_rename([(str(source), str(target))])
            log = create_rollback_log(pairs, str(root / "logs"))

            results = execute_rollback(log)

            self.assertEqual(results["errors"], [])
            self.assertTrue(source.exists())
            self.assertFalse(target.exists())

    def test_duplicate_targets_abort_before_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first, second, target = root / "a.jpg", root / "b.jpg", root / "x.jpg"
            first.write_bytes(b"a")
            second.write_bytes(b"b")
            results, pairs = execute_rename([(str(first), str(target)), (str(second), str(target))])
            self.assertTrue(results["errors"])
            self.assertEqual(pairs, [])
            self.assertTrue(first.exists() and second.exists())

    def test_noop_is_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "same.jpg"
            source.write_bytes(b"same")
            results, pairs = execute_rename([(str(source), str(source))])
            self.assertEqual(results["success"], 1)
            self.assertEqual(results["errors"], [])
            self.assertEqual(source.read_bytes(), b"same")
            self.assertEqual(pairs, [(str(source), str(source))])


class BatchAndFilesTests(unittest.TestCase):
    def test_batch_tokens_and_invalid_names(self):
        files = [Path("foto.jpg")]
        mapping = generate_batch_mapping(files, "[NOME]_##", start_index=3)
        self.assertEqual(Path(mapping[0][1]).name, "foto_03.jpg")
        with self.assertRaises(ValueError):
            generate_batch_mapping(files, "nome/inválido")

    def test_natural_and_modified_order(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            ten, two = root / "foto10.jpg", root / "foto2.jpg"
            ten.write_bytes(b"x")
            two.write_bytes(b"x")
            os.utime(ten, (1, 1))
            os.utime(two, (2, 2))
            self.assertEqual([p.name for p in get_valid_images(folder)], ["foto2.jpg", "foto10.jpg"])
            self.assertEqual([p.name for p in get_valid_images(folder, "modified")], ["foto10.jpg", "foto2.jpg"])

    def test_recursive_discovery_and_metadata_tokens(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            nested = root / "evento"
            nested.mkdir()
            image = nested / "foto.jpg"
            image.write_bytes(b"x")
            files = get_valid_images(folder, recursive=True)
            self.assertEqual(files, [image])
            mapping = generate_batch_mapping(
                files,
                "[PASTA]_[EXT]_##",
                start_index=10,
                increment=5,
            )
            self.assertEqual(Path(mapping[0][1]).name, "evento_jpg_10.jpg")


class AlignmentPerformanceTests(unittest.TestCase):
    def test_swap_is_constant_time_and_undoable(self):
        mapping = [
            (Path(f"origin-{index}.jpg"), Path(f"destination-{index}.jpg"))
            for index in range(10_000)
        ]
        model = AlignmentModel(mapping)
        started = time.perf_counter()
        for _ in range(1_000):
            model.swap(12, 9_876)
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 0.25)
        self.assertTrue(model.can_undo)
        self.assertEqual(model.undo(), (12, 9_876))

    def test_thumbnail_loader_respects_bounds(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as folder:
            image_path = Path(folder) / "large.jpg"
            Image.new("RGB", (1600, 900), "navy").save(image_path)
            thumbnail = load_thumbnail(image_path)
            self.assertLessEqual(thumbnail.width, 160)
            self.assertLessEqual(thumbnail.height, 120)
            self.assertEqual(thumbnail.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
