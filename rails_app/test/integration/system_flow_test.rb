require "test_helper"
require "webmock/minitest"

class IntegrationTest < ActionDispatch::IntegrationTest
  setup do
    # Mock Spine Service responses
    stub_request(:get, "http://spine:8000/docs").to_return(status: 200)
  end

  test "health check" do
    get "/up"
    assert_response :success
  end
  
  # Note: Real integration requires running containers.
  # This file is just a placeholder to run `rails test` if needed.
end
