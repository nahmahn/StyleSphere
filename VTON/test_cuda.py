import torch

def test_cuda():
    print('PyTorch version:', torch.__version__)
    cuda_available = torch.cuda.is_available()
    print('CUDA available:', cuda_available)
    if cuda_available:
        print('CUDA device count:', torch.cuda.device_count())
        print('Current device:', torch.cuda.current_device())
        print('Device name:', torch.cuda.get_device_name(torch.cuda.current_device()))
        x = torch.rand(3, 3).cuda()
        print('Tensor on CUDA:', x)
    else:
        print('CUDA is not available on this system.')

if __name__ == '__main__':
    test_cuda()
