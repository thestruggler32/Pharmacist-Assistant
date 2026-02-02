# New API endpoints for annotations and approvals

@app.route('/api/prescriptions/<id>/annotate', methods=['POST'])
@jwt_required()
def add_annotation(id):
    """Add or update annotations for a prescription"""
    current_user = get_jwt_identity()
    data = request.json
    
    try:
        annotations = data.get('annotations', [])
        prescription_db.add_annotation(id, {
            'annotations': annotations,
            'annotated_by': current_user['email'],
            'annotated_at': datetime.now().isoformat()
        })
        
        return jsonify({"msg": "Annotations saved", "count": len(annotations)})
    except Exception as e:
        return jsonify({"msg": f"Failed to save annotations: {str(e)}"}), 500

@app.route('/api/prescriptions/<id>/annotations', methods=['GET'])
@jwt_required()
def get_annotations(id):
    """Get all annotations for a prescription"""
    annotations = prescription_db.get_annotations(id)
    return jsonify({"annotations": annotations})

@app.route('/api/prescriptions/<id>/annotated-image', methods=['GET'])
@jwt_required()
def get_annotated_image(id):
    """Get prescription image with annotations overlaid"""
    try:
        prescription = prescription_db.get_prescription(id)
        if not prescription:
            return jsonify({"msg": "Prescription not found"}), 404
        
        image_url = prescription.get('image_url', '').lstrip('/')
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_url))
        
        annotations = prescription_db.get_annotations(id)
        annotation_data = annotations[-1].get('annotations', []) if annotations else []
        
        annotated_base64 = create_annotated_image(image_path, annotation_data)
        
        return jsonify({
            "annotated_image": annotated_base64,
            "annotation_count": len(annotation_data)
        })
    except Exception as e:
        return jsonify({"msg": f"Failed to create annotated image: {str(e)}"}), 500

@app.route('/api/approvals', methods=['GET'])
@jwt_required()
def get_approvals():
    """Get pending approval requests for pharmacist"""
    current_user = get_jwt_identity()
    pharmacist_id = current_user.get('email') if current_user.get('role') == 'pharmacist' else None
    
    approvals = prescription_db.get_pending_approvals(pharmacist_id)
    
    # Enrich with prescription data
    enriched_approvals = []
    for approval in approvals:
        prescription = prescription_db.get_prescription(approval['prescription_id'])
        enriched_approvals.append({
            **approval,
            'prescription': prescription
        })
    
    return jsonify({"approvals": enriched_approvals, "count": len(enriched_approvals)})

@app.route('/api/approvals/<approval_id>/submit', methods=['POST'])
@jwt_required()
def submit_approval(approval_id):
    """Submit approval review with corrections"""
    current_user = get_jwt_identity()
    if current_user.get('role') not in ['pharmacist']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.json
    status = data.get('status', 'approved')  # 'approved' or 'rejected'
    corrected_medicines = data.get('corrected_medicines')
    
    updated_approval = prescription_db.update_approval(
        approval_id,
        status,
        current_user['email'],
        corrected_medicines
    )
    
    if updated_approval:
        return jsonify(updated_approval)
    else:
        return jsonify({"msg": "Approval not found"}), 404
