# Copyright (c) OpenMMLab. All rights reserved.
import types

from xtuner._lite import get_logger

logger = get_logger()


def _dispatch_forward_fn(module, dispatch_fn):
    module.forward = types.MethodType(dispatch_fn, module)


def  _dispatch_qwen2_attn_flash_forward(module):
    assert module.__class__.__name__ in ['Qwen2FlashAttention2', 'Qwen2Attention', 'Qwen2SdpaAttention']
    from .qwen2 import qwen2_attn_flash_forward
    from xtuner._lite.accelerate import varlen_attn_is_available
    if varlen_attn_is_available():
        _dispatch_forward_fn(module, qwen2_attn_flash_forward)
        return qwen2_attn_flash_forward.__name__


def _dispatch_internlm2_varlen_attn_forward(module):
    assert module.__class__.__name__ in ['InternLM2FlashAttention2', 'InternLM2Attention', 'InternLM2SdpaAttention']
    from .internlm2 import internlm2_varlen_attn_forward
    from xtuner._lite.accelerate import varlen_attn_is_available
    if varlen_attn_is_available():
        _dispatch_forward_fn(module, internlm2_varlen_attn_forward)
        return internlm2_varlen_attn_forward.__name__

def _dispatch_internlm3_varlen_self_attn_forward(module):
    assert module.__class__.__name__ in ['InternLM3FlashSelfAttention2']
    from .internlm3 import internlm3_self_attn_forward
    from xtuner._lite.accelerate import varlen_attn_is_available
    if varlen_attn_is_available():
        _dispatch_forward_fn(module, internlm3_self_attn_forward)
        return internlm3_self_attn_forward.__name__

def _dispatch_internlm3_varlen_cross_attn_forward(module):
    assert module.__class__.__name__ in ['InternLM3FlashCrossAttention2']
    from .internlm3 import internlm3_cross_attn_forward
    from xtuner._lite.accelerate import varlen_attn_is_available
    if varlen_attn_is_available():
        _dispatch_forward_fn(module, internlm3_cross_attn_forward)
        return internlm3_cross_attn_forward.__name__

def _dispatch_internlm3_cross_decoder_forward(module):
    assert module.__class__.__name__ == 'InternLM3CrossDecoder'
    from .internlm3 import internlm3_cross_decoder_forward
    _dispatch_forward_fn(module, internlm3_cross_decoder_forward)
    return internlm3_cross_decoder_forward.__name__


def _dispatch_internlm2_reward_forward(module):
    assert module.__class__.__name__ == 'InternLM2ForRewardModel'
    from .internlm2 import internlm2_reward_forward
    _dispatch_forward_fn(module, internlm2_reward_forward)
    return internlm2_reward_forward.__name__


def _dispatch_clip_attn_forward(module):
    assert module.__class__.__name__ == 'CLIPAttention'
    from .clip import clip_flash_attn_forward
    _dispatch_forward_fn(module, clip_flash_attn_forward)
    return clip_flash_attn_forward.__name__


def _dispatch_rms_norm_forward(module):
    from .._fused import rms_norm_forward
    _dispatch_forward_fn(module, rms_norm_forward)
    return rms_norm_forward.__name__


DISPATCH_MAP = {
    'Qwen2RMSNorm': _dispatch_rms_norm_forward,
    'Qwen2FlashAttention2': _dispatch_qwen2_attn_flash_forward,
    'Qwen2Attention': _dispatch_qwen2_attn_flash_forward,
    'Qwen2SdpaAttention': _dispatch_qwen2_attn_flash_forward,
    'InternLM2Attention': _dispatch_internlm2_varlen_attn_forward,
    'InternLM2SdpaAttention': _dispatch_internlm2_varlen_attn_forward,
    'InternLM2FlashAttention2': _dispatch_internlm2_varlen_attn_forward,
    'CLIPAttention': _dispatch_clip_attn_forward,
    'InternLM2ForRewardModel': _dispatch_internlm2_reward_forward,
    'InternLM2RMSNorm': _dispatch_rms_norm_forward,
    'InternLM3RMSNorm': _dispatch_rms_norm_forward,
    'InternLM3CrossDecoder': _dispatch_internlm3_cross_decoder_forward,
    'InternLM3FlashSelfAttention2': _dispatch_internlm3_varlen_self_attn_forward,
    'InternLM3FlashCrossAttention2': _dispatch_internlm3_varlen_cross_attn_forward
}


def dispatch_hf_code(model):
    from xtuner._lite import get_logger
    logger = get_logger()

    for name, module in model.named_modules():
        cls_name = module.__class__.__name__
        if cls_name in DISPATCH_MAP:
            dispatched = DISPATCH_MAP[cls_name](module)
            if dispatched is not None:
                logger.debug(
                    f'Dispatch {name}({cls_name}) forward to `{dispatched}`')