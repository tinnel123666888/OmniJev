import unittest
import torch
from mso.action import ActionExpert, ActionSpace, ChunkMixture, DualRoute, chunk_nll


class ActionTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(17)
        self.space = ActionSpace("arm", ("dx", "dy"), (-2., -3.), (2., 3.), 25, horizon=3)

    def test_masked_tail_does_not_change_loss_or_gradient(self):
        head = ChunkMixture(8, self.space)
        pred = head(torch.randn(2, 8))
        y = torch.zeros(2, 3, 2)
        mask = torch.tensor([[1, 1, 0], [1, 0, 0]], dtype=torch.bool)
        a = chunk_nll(pred, y, mask)
        y[~mask] = float("nan")
        b = chunk_nll(pred, y, mask)
        torch.testing.assert_close(a, b)
        b.backward()
        self.assertTrue(all(torch.isfinite(p.grad).all() for p in head.parameters()))

    def test_mode_selection_does_not_average_opposite_commands(self):
        head = ChunkMixture(8, self.space, components=2)
        p = {"logits": torch.tensor([[0., 1.]]), "means": torch.tensor([[[[-1., -1.]] * 3, [[1., 1.]] * 3]])}
        torch.testing.assert_close(head.command(p), torch.tensor([[[2., 3.]] * 3]))

    def test_gradient_cannot_reach_frozen_features(self):
        model = ActionExpert(8, 4, [self.space], {"game": ["left", "right"]}, hidden=16)
        f = torch.randn(2, 8, requires_grad=True)
        y = model(f, torch.zeros(2, 4), torch.zeros(2, 4), "arm", "continuous")
        chunk_nll(y, torch.zeros(2, 3, 2), torch.ones(2, 3)).backward()
        self.assertIsNone(f.grad)
        self.assertIsNotNone(model.visual[1].weight.grad)
        with self.assertRaises(ValueError):
            model(f, torch.zeros(2, 4), torch.zeros(2, 4), "game", "continuous")

    def test_original_general_arguments_and_result_are_unchanged(self):
        state, questions, result = object(), object(), object()
        calls = []
        def general(s, q):
            calls.append((s, q))
            return result
        def action(*a, **kw):
            raise AssertionError("General request reached the action route")
        router = DualRoute(general, action)
        self.assertIs(router(state, questions), result)
        self.assertEqual(calls, [(state, questions)])
        with self.assertRaises(ValueError):
            router(state, mode="continuous", action_space="arm")


if __name__ == "__main__":
    unittest.main()
