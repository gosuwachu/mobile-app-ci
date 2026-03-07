from unittest.mock import patch

from company.ci.build_name import get_build_name


class TestGetBuildName:
    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-build.Jenkinsfile",
        "COMMIT_SHA": "abc1234567890",
        "PR_NUMBER": "42",
        "CI_BRANCH": "main",
        "BUILD_NUMBER": "7",
    })
    def test_full_pr_build(self):
        assert get_build_name() == "#7 ios-build abc1234 PR#42"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/android/android-linter.Jenkinsfile",
        "COMMIT_SHA": "def5678",
        "CI_BRANCH": "main",
        "BUILD_NUMBER": "12",
    }, clear=True)
    def test_branch_build_no_pr(self):
        assert get_build_name() == "#12 android-linter def5678"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-build.Jenkinsfile",
        "COMMIT_SHA": "abc1234",
        "PR_NUMBER": "5",
        "CI_BRANCH": "feature/new-steps",
        "BUILD_NUMBER": "3",
    })
    def test_non_main_ci_branch(self):
        assert get_build_name() == "#3 ios-build abc1234 PR#5 [ci:feature/new-steps]"

    @patch.dict("os.environ", {
        "PR_NUMBER": "42",
        "BUILD_NUMBER": "9",
    }, clear=True)
    def test_name_override(self):
        assert get_build_name("ios-ui-tests") == "#9 ios-ui-tests PR#42"

    @patch.dict("os.environ", {"BUILD_NUMBER": "1"}, clear=True)
    def test_minimal(self):
        assert get_build_name() == "#1 build"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-deploy.Jenkinsfile",
        "COMMIT_SHA": "aaa",
    }, clear=True)
    def test_no_build_number(self):
        assert get_build_name() == "ios-deploy aaa"
