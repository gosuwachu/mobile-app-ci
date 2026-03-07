from unittest.mock import patch

from company.ci.build_name import get_build_name


class TestGetBuildName:
    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-build.Jenkinsfile",
        "COMMIT_SHA": "abc1234567890",
        "CHANGE_ID": "42",
        "CI_BRANCH": "main",
        "BUILD_NUMBER": "7",
    })
    def test_full_pr_build(self):
        assert get_build_name() == "#7 abc1234 PR#42 ios-build"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/android/android-linter.Jenkinsfile",
        "COMMIT_SHA": "def5678",
        "CI_BRANCH": "main",
        "BUILD_NUMBER": "12",
    }, clear=True)
    def test_branch_build_no_pr(self):
        assert get_build_name() == "#12 def5678 android-linter"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-build.Jenkinsfile",
        "COMMIT_SHA": "abc1234",
        "CHANGE_ID": "5",
        "CI_BRANCH": "feature/new-steps",
        "BUILD_NUMBER": "3",
    })
    def test_non_main_ci_branch(self):
        assert get_build_name() == "#3 abc1234 PR#5 ios-build [ci:feature/new-steps]"

    @patch.dict("os.environ", {
        "CHANGE_ID": "42",
        "BUILD_NUMBER": "9",
    }, clear=True)
    def test_name_override(self):
        assert get_build_name("ios-ui-tests") == "#9 PR#42 ios-ui-tests"

    @patch.dict("os.environ", {"BUILD_NUMBER": "1"}, clear=True)
    def test_minimal(self):
        assert get_build_name() == "#1"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-deploy.Jenkinsfile",
        "COMMIT_SHA": "aaa",
    }, clear=True)
    def test_no_build_number(self):
        assert get_build_name() == "aaa ios-deploy"

    @patch.dict("os.environ", {
        "GIT_COMMIT": "abc1234567890",
        "CHANGE_ID": "7",
        "BUILD_NUMBER": "3",
    }, clear=True)
    def test_fallback_to_git_commit(self):
        assert get_build_name() == "#3 abc1234 PR#7"

    @patch.dict("os.environ", {
        "JENKINSFILE": "ci/ios/ios-deploy.Jenkinsfile",
        "COMMIT_SHA": "abc1234",
        "BUILD_NUMBER": "5",
        "CONTEXT_JSON": '{"job_name": "mobile-app-support/omnibus", "build_number": "42"}',
    }, clear=True)
    def test_context_json_in_display_name(self):
        assert get_build_name() == "#5 abc1234 ios-deploy [from omnibus #42]"
