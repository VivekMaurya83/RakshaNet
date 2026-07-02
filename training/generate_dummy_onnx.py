import onnx
from onnx import helper, TensorProto
from pathlib import Path

def create_dummy_onnx(output_path_str: str):
    output_path = Path(output_path_str)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Input Node: shape (batch_size, 224, 224, 3)
    input_node = helper.make_tensor_value_info('input_image', TensorProto.FLOAT, [None, 224, 224, 3])
    
    # 2. Output Node: shape (batch_size, 2)
    output_node = helper.make_tensor_value_info('output', TensorProto.FLOAT, [None, 2])
    
    # 3. ReduceMean node: Pool spatial dims (height=224, width=224) to get (batch_size, 3)
    reduce_node = helper.make_node(
        'ReduceMean',
        inputs=['input_image'],
        outputs=['reduced_tensor'],
        axes=[1, 2],
        keepdims=False
    )
    
    # 4. Define Weights & Biases for Gemm
    # To balance Genuine and Counterfeit based on mean Red channel intensity:
    # class 0 (Counterfeit) logit = 1.0 * R
    # class 1 (Genuine) logit = 0.5
    weights_data = [
        1.0, 0.0,
        0.0, 0.0,
        0.0, 0.0
    ]
    weights_tensor = helper.make_tensor(
        name='W',
        data_type=TensorProto.FLOAT,
        dims=[3, 2],
        vals=weights_data
    )
    
    bias_data = [0.0, 0.5]
    bias_tensor = helper.make_tensor(
        name='B',
        data_type=TensorProto.FLOAT,
        dims=[2],
        vals=bias_data
    )
    
    # 5. Gemm node (Matrix multiplication + bias)
    gemm_node = helper.make_node(
        'Gemm',
        inputs=['reduced_tensor', 'W', 'B'],
        outputs=['output']
    )
    
    # 6. Assemble Graph
    graph = helper.make_graph(
        nodes=[reduce_node, gemm_node],
        name='rakshanet_counterfeit_model',
        inputs=[input_node],
        outputs=[output_node],
        initializer=[weights_tensor, bias_tensor]
    )
    
    # 7. Create ONNX Model
    model = helper.make_model(graph, producer_name='rakshanet_edge_model')
    model.opset_import[0].version = 13
    
    # 8. Save to disk
    onnx.save(model, str(output_path))
    print(f"✓ Balanced dummy model.onnx saved to: {output_path}")

if __name__ == "__main__":
    create_dummy_onnx("models/counterfeit/model.onnx")
