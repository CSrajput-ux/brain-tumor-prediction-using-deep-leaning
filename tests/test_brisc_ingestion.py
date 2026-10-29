from pathlib import Path

from src.data.brisc_dataset import CLASS_IDS, read_brisc_records


def test_brisc_ingestion_reads_only_classification_records(tmp_path: Path) -> None:
    root = tmp_path
    (root / "classification_task/train/glioma").mkdir(parents=True)
    (root / "segmentation_task/train/images").mkdir(parents=True)
    (root / "segmentation_task/train/masks").mkdir(parents=True)
    (root / "classification_task/train/glioma/a.jpg").write_bytes(b"image")
    (root / "segmentation_task/train/images/a.jpg").write_bytes(b"image")
    (root / "segmentation_task/train/masks/a.png").write_bytes(b"mask")
    (root / "manifest.csv").write_text(
        "relative_path,filename,task,split,index,tumor_code,tumor_label,plane_code,plane_label,sequence,is_mask,linked_image,width,height,file_size_bytes,sha256\n"
        "classification_task/train/glioma/a.jpg,a.jpg,classification,train,1,gl,glioma,ax,axial,T1,False,,1,1,1,x\n"
        "segmentation_task/train/images/a.jpg,a.jpg,segmentation,train,1,gl,glioma,ax,axial,T1,False,,1,1,1,x\n"
        "segmentation_task/train/masks/a.png,a.png,segmentation,train,1,gl,glioma,ax,axial,T1,True,a.jpg,1,1,1,x\n",
        encoding="utf-8",
    )
    records = list(read_brisc_records(root))
    assert len(records) == 1
    assert records[0]["class_id"] == CLASS_IDS["glioma"]
    assert records[0]["mask_pair_status"] == "paired"
