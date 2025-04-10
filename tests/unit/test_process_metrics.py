import datetime

from core.parsers.process_metric_calculation import ProcessMetrics


def test_process_metrics_all_metrics():
    """
    Teste les différentes méthodes de la classe `ProcessMetrics` pour vérifier
    qu'elles calculent correctement les métriques de processus.

    Scénario :
        - Une contribution actuelle et un historique de contributions précédentes sont fournis.
        - Les contributions incluent des informations sur les auteurs, les dates, les commits,
          et les blocs Terraform.

    Assertions :
        - Vérifie que les métriques calculées (comme `num_defects_in_block_before`,
          `num_devs`, `code_ownership`, etc.) retournent les valeurs attendues.
        - Vérifie que la méthode `resume_process_metrics` retourne un résumé contenant
          toutes les métriques calculées.

    Returns:
        None
    """
    contribution = {
        "author": "alice",
        "file": "main.tf",
        "block_identifiers": "aws_s3_bucket.mybucket",
        "commit": "c4",
        "date": datetime.datetime(2025, 3, 23),
        "exp": 4,
        "isResource": 1,
        "isData": 0,
        "block": "aws_s3_bucket",
        "block_id": "aws_s3_bucket.mybucket",
    }

    previous = [
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 20),
            "fault_prone": 0,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c2",
            "date": datetime.datetime(2025, 3, 21),
            "fault_prone": 1,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "bob",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c3",
            "date": datetime.datetime(2025, 3, 22),
            "fault_prone": 1,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.other",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 19),
            "fault_prone": 0,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.other",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "module.vpc",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 18),
            "fault_prone": 0,
            "block": "module",
            "block_id": "module.vpc",
        },
    ]

    pm = ProcessMetrics(contribution, previous)

    assert pm.num_defects_in_block_before() == 2
    assert pm.num_devs() == 2
    assert pm.num_commits() == 3
    assert pm.code_ownership() == 0.5
    assert pm.get_author_bexp() == 3
    assert pm.get_author_sexp() == 4
    assert pm.kexp() == 2
    assert pm.num_same_blocks_with_different_names_changed_before() == 3
    assert pm.num_unique_change() == 2
    assert round(pm.get_author_rexp(), 2) == round((1 / 4 + 1 / 3 + 1 / 5 + 1 / 6), 2)
    assert round(pm.age(), 2) == round((3 + 2 + 1) / 3, 2)
    assert pm.time_interval() == 1
    assert len(pm.resume_process_metrics()) == 13


def test_resume_process_metrics_keys():
    """
    Teste la méthode `resume_process_metrics` pour vérifier qu'elle retourne
    un dictionnaire contenant toutes les clés attendues.

    Scénario :
        - Une contribution actuelle et un historique de contributions précédentes sont fournis.
        - La méthode `resume_process_metrics` est appelée pour générer un résumé des métriques.

    Assertions :
        - Vérifie que toutes les clés attendues sont présentes dans le résumé retourné.

    Returns:
        None
    """
    contribution = {
        "author": "alice",
        "file": "main.tf",
        "block_identifiers": "aws_s3_bucket.mybucket",
        "commit": "c4",
        "date": datetime.datetime(2025, 3, 23),
        "exp": 4,
        "isResource": 1,
        "isData": 0,
        "block": "aws_s3_bucket",
        "block_id": "aws_s3_bucket.mybucket",
    }

    previous = [
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 20),
            "fault_prone": 0,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c2",
            "date": datetime.datetime(2025, 3, 21),
            "fault_prone": 1,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "bob",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.mybucket",
            "commit": "c3",
            "date": datetime.datetime(2025, 3, 22),
            "fault_prone": 1,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.mybucket",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "aws_s3_bucket.other",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 19),
            "fault_prone": 0,
            "block": "aws_s3_bucket",
            "block_id": "aws_s3_bucket.other",
        },
        {
            "author": "alice",
            "file": "main.tf",
            "block_identifiers": "module.vpc",
            "commit": "c1",
            "date": datetime.datetime(2025, 3, 18),
            "fault_prone": 0,
            "block": "module",
            "block_id": "module.vpc",
        },
    ]

    pm = ProcessMetrics(contribution, previous)
    metrics = pm.resume_process_metrics()

    expected_keys = {
        "ndevs",
        "ncommits",
        "code_ownership",
        "exp",
        "rexp",
        "sexp",
        "bexp",
        "age",
        "time_interval",
        "num_defects_before",
        "num_same_instances_changed_before",
        "kexp",
        "num_unique_change",
    }

    assert set(metrics.keys()) == expected_keys
