import pytest
from unittest.mock import patch, MagicMock
import orchestrator

@pytest.fixture
def mock_subprocess_run():
    with patch("orchestrator.subprocess.run") as mock_run:
        yield mock_run

@pytest.fixture
def mock_os_path_exists():
    with patch("orchestrator.os.path.exists") as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_shutil_rmtree():
    with patch("orchestrator.shutil.rmtree") as mock_rmtree:
        yield mock_rmtree

@pytest.fixture
def mock_os_path_abspath():
    with patch("orchestrator.os.path.abspath") as mock_abspath:
        yield mock_abspath

def test_clone_repo_happy_path(mock_subprocess_run, mock_os_path_exists, mock_shutil_rmtree):
    mock_os_path_exists.return_value = True

    orchestrator.clone_repo()

    mock_os_path_exists.assert_called_once_with(orchestrator.CLONE_DIR)
    mock_shutil_rmtree.assert_called_once_with(orchestrator.CLONE_DIR)
    mock_subprocess_run.assert_called_once_with(
        f"git clone {orchestrator.REPO_URL} {orchestrator.CLONE_DIR}",
        shell=True,
        check=True,
        cwd=None,
    )

def test_clone_repo_edge_case_no_existing_dir(mock_subprocess_run, mock_os_path_exists, mock_shutil_rmtree):
    mock_os_path_exists.return_value = False

    orchestrator.clone_repo()

    mock_os_path_exists.assert_called_once_with(orchestrator.CLONE_DIR)
    mock_shutil_rmtree.assert_not_called()
    mock_subprocess_run.assert_called_once_with(
        f"git clone {orchestrator.REPO_URL} {orchestrator.CLONE_DIR}",
        shell=True,
        check=True,
        cwd=None,
    )

def test_checkout_branch_happy_path(mock_subprocess_run):
    orchestrator.checkout_branch()

    mock_subprocess_run.assert_called_once_with(
        "git checkout -b test || git checkout test",
        shell=True,
        check=True,
        cwd=orchestrator.CLONE_DIR,
    )

def test_run_docker_happy_path(mock_subprocess_run, mock_os_path_abspath):
    mock_os_path_abspath.return_value = "/absolute/path/to/repo"

    orchestrator.run_docker()

    mock_os_path_abspath.assert_called_once_with(orchestrator.CLONE_DIR)
    mock_subprocess_run.assert_called_once_with(
        """
    docker run --rm \
    -v repo:/repo \
    ai-sandbox
    """,
        shell=True,
        check=True,
    )

def test_commit_and_push_happy_path(mock_subprocess_run):
    orchestrator.commit_and_push()

    mock_subprocess_run.assert_any_call("git add .", shell=True, check=True, cwd=orchestrator.CLONE_DIR)
    mock_subprocess_run.assert_any_call(
        'git commit -m "AI Maintainer update" || true', shell=True, check=True, cwd=orchestrator.CLONE_DIR
    )
    mock_subprocess_run.assert_any_call("git push origin test", shell=True, check=True, cwd=orchestrator.CLONE_DIR)