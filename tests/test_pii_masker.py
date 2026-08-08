from auditfleet.core.pii_masker import mask_pii


def test_masks_common_pii():
    result = mask_pii("mail=a@example.com phone=0912-345-678 card=4111 1111 1111 1111")
    assert "a@example.com" not in result.text
    assert "0912-345-678" not in result.text
    assert "4111 1111 1111 1111" not in result.text
    assert sum(result.counts.values()) >= 3
