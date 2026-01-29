require 'faraday'
require 'faraday/multipart'

class SpineClient
  BASE_URL = ENV.fetch('SPINE_URL', 'http://spine:8000')

  def self.connection
    Faraday.new(url: BASE_URL) do |f|
      f.request :multipart
      f.request :url_encoded
      f.adapter Faraday.default_adapter
    end
  end

  def self.health
    connection.get('/docs')
  end

  def self.upload(file_path, original_filename)
     # Using FilePart for automated MIME type handling if possible, or explicit
     payload = {
       file: Faraday::Multipart::FilePart.new(
         file_path,
         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
         original_filename
       )
     }
     
     connection.post('/upload', payload)
  end

  def self.get_tree(contract_id)
    connection.get("/contract/#{contract_id}/tree")
  end

  def self.query(contract_id, query_text)
    connection.post("/contract/#{contract_id}/query", { query: query_text }.to_json, 'Content-Type' => 'application/json')
  end

  def self.refactor(contract_id, node_id, action, params={})
     body = {
       node_id_xml: node_id,
       action: action
     }.merge(params)
     
     connection.post("/contract/#{contract_id}/refactor", body.to_json, 'Content-Type' => 'application/json')
  end

  def self.edit_document(document_id, operations)
    # Generic entry point for the "Loose Akoma" Engine
    # operations: Array of { type: "update_text"|"split", id: "uuid", ... }
    connection.post("/api/documents/#{document_id}/edit", operations.to_json, 'Content-Type' => 'application/json')
  end

  def self.analyze_logic(file_path, original_filename, playbook_json)
    payload = {
      file: Faraday::Multipart::FilePart.new(
        file_path,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        original_filename
      ),
      playbook: playbook_json
    }
    
    connection.post('/analyze_logic', payload)
  end
end
