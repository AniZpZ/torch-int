import torch
from torch_int._CUDA import linear_a8_w8_b32_o32, linear_relu_a8_w8_b8_o8, linear_a8_w8_b8_o8
from icecream import ic


@torch.no_grad()
def test_quant_linear_a8_w8_b32_o32():
    B, M, N = 128, 512, 1024
    weight = torch.randint(-128, 127, (N, M), dtype=torch.int8)
    bias = torch.randint(-65536, 65535, (N,), dtype=torch.int32)
    x = torch.randint(-128, 127, (B, M), dtype=torch.int8)
    linear = torch.nn.Linear(M, N, bias=True)
    linear.weight.data = weight.float()
    linear.bias.data = bias.float()
    y_gt = linear(x.float())
    y = linear_a8_w8_b32_o32(x.cuda(), weight.cuda(), bias.cuda())
    ic(torch.allclose(y_gt, y.float().cpu(), atol=1e-3))


@torch.no_grad()
def test_quant_linear_a8_w8_b8_o8():
    B, M, N = 128, 512, 1024
    weight = torch.randint(-128, 127, (N, M), dtype=torch.int8)
    bias = torch.randint(-128, 127, (N,), dtype=torch.int8)
    x = torch.randint(-128, 127, (B, M), dtype=torch.int8)
    output_scale, bias_scale = 0.001, 0.01
    linear = torch.nn.Linear(M, N, bias=True)
    linear.weight.data = weight.float() * output_scale
    linear.bias.data = bias.float() * bias_scale
    y_gt = linear(x.float()).clamp(-128, 127).round().long()
    y = linear_a8_w8_b8_o8(x.cuda(), weight.cuda(),
                           bias.cuda(), output_scale, bias_scale).cpu().long()
    ic(torch.allclose(y_gt.float(), y.float().cpu(), atol=1))


@torch.no_grad()
def test_quant_linear_relu_a8_w8_b8_o8():
    B, M, N = 2, 16, 16
    weight = torch.randint(-128, 127, (N, M), dtype=torch.int8)
    bias = torch.randint(-128, 127, (N,), dtype=torch.int8)
    x = torch.randint(-128, 127, (B, M), dtype=torch.int8)
    output_scale, bias_scale = 0.001, 0.01
    linear = torch.nn.Linear(M, N, bias=True)
    linear.weight.data = weight.float() * output_scale
    linear.bias.data = bias.float() * bias_scale
    y_gt = linear(x.float())
    ic(y_gt)
    y_gt = y_gt.clamp(0, 127).round().long()
    ic(y_gt)
    y = linear_relu_a8_w8_b8_o8(x.cuda(), weight.cuda(),
                                bias.cuda(), output_scale, bias_scale).cpu().long()
    ic(y)
    ic(torch.allclose(y_gt.float(), y.float().cpu(), atol=1))


if __name__ == '__main__':
    # print('test_quant_linear_a8_w8_b32_o32')
    # test_quant_linear_a8_w8_b32_o32()
    # print('test_quant_linear_a8_w8_b8_o8')
    # test_quant_linear_a8_w8_b8_o8()
    print('test_quant_linear_relu_a8_w8_b8_o8')
    test_quant_linear_relu_a8_w8_b8_o8()