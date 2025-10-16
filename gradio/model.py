import paddle
from paddle.static import InputSpec

# 加载模型
model = paddle.jit.load("C:/Users/lenovo/PaddleX/output/best_model")

# 设置输入规格
input_spec = [InputSpec(shape=[None, 3, 416, 416], dtype="float32")]

# 导出模型
paddle.jit.save(
    model,
    path="C:/Users/lenovo/PaddleX/output/inference_model",
    input_spec=input_spec
)