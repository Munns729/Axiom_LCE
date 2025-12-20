class DocumentsController < ApplicationController
  def create
    uploaded_file = params[:file]
    if uploaded_file.nil?
      render json: { error: "No file provided" }, status: :bad_request
      return
    end

    # Save to tempfile to pass to Spine
    # In a real app we might stream it, but saving is safer for multipart
    # ActiveStorage puts it in tmp usually.
    
    # We use SpineClient to push it
    response = SpineClient.upload(uploaded_file.path, uploaded_file.original_filename)
    
    if response.success?
      data = JSON.parse(response.body)
      render json: data, status: :ok
    else
      render json: { error: "Spine Upload Failed", details: response.body }, status: :unprocessable_entity
    end
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def show
    contract_id = params[:id]
    response = SpineClient.get_tree(contract_id)
    if response.success?
      render json: JSON.parse(response.body)
    else
      render json: { error: "Failed to fetch tree", status: response.status }, status: :bad_request
    end
  end

  def query
    contract_id = params[:id]
    query_text = params[:query]
    
    response = SpineClient.query(contract_id, query_text)
    if response.success?
      render json: JSON.parse(response.body)
    else
      render json: { error: "Query failed" }, status: :bad_request
    end
  end

  def refactor
    contract_id = params[:id]
    # action, node_id_xml, etc
    node_id = params[:node_id_xml]
    action = params[:action]
    
    response = SpineClient.refactor(contract_id, node_id, action, params.except(:id, :controller, :action))
    
    if response.success?
      render json: JSON.parse(response.body)
    else
      render json: { error: "Refactor failed" }, status: :bad_request
    end
  end

  def analyze_logic
    uploaded_file = params[:file]
    if uploaded_file.nil?
      render json: { error: "No file provided" }, status: :bad_request
      return
    end

    # Handle playbook: could be a JSON string or a hash
    playbook_val = params[:playbook]
    playbook_json = playbook_val.is_a?(Hash) ? playbook_val.to_json : playbook_val.to_s

    response = SpineClient.analyze_logic(uploaded_file.path, uploaded_file.original_filename, playbook_json)

    if response.success?
      render json: JSON.parse(response.body), status: :ok
    else
      render json: { error: "Analysis failed", details: response.body }, status: :unprocessable_entity
    end
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end
end
