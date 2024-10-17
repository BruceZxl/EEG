import torch
import torch.nn as nn
import torch.nn.functional as F


class SupConLoss_clear(nn.Module):
    def __init__(self, temperature=0.07):
        super(SupConLoss_clear, self).__init__()
        self.temperature = temperature

    def forward(self, features, labels):
        device = (torch.device('cuda')
                  if features.is_cuda
                  else torch.device('cpu'))

        batch_size = features.shape[0]
        labels = labels.contiguous().view(-1, 1)
        mask = torch.eq(labels, labels.t()).float().to(device)

        anchor_dot_contrast = torch.div(  # 按位除
            torch.matmul(features, features.t()),
            self.temperature)

        # normalize the logits for numerical stability
        logits_max, _ = torch.max(anchor_dot_contrast, dim=1, keepdim=True)
        logits = anchor_dot_contrast - logits_max.detach()
        # mask-out self-contrast cases
        logits_mask = torch.scatter(
            torch.ones_like(mask),
            1,
            torch.arange(batch_size).view(-1, 1).to(device),
            0
        )
        mask = mask * logits_mask
        single_samples = (mask.sum(1) == 0).float()

        # compute log_prob
        exp_logits = torch.exp(logits) * logits_mask

        log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-20)

        # compute mean of log-likelihood over positive
        # invoid to devide the zero
        mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + single_samples)

        # loss
        # filter those single sample
        loss = - mean_log_prob_pos * (1 - single_samples)
        loss = loss.sum() / (loss.shape[0] - single_samples.sum())

        return loss


class SupConLoss_seq(nn.Module):
    def __init__(self, temperature=0.07):
        super(SupConLoss_seq, self).__init__()
        self.temperature = temperature

    def forward(self, features, labels):
        device = (torch.device('cuda')
                  if features.is_cuda
                  else torch.device('cpu'))

        batch_size = features.shape[0]

        anchor_dot_contrast = torch.div(  # 按位除
            torch.matmul(features, features.t()),
            self.temperature)

        # normalize the logits for numerical stability
        logits_max, _ = torch.max(anchor_dot_contrast, dim=1, keepdim=True)
        logits = anchor_dot_contrast - logits_max.detach()

        minute_loss = torch.zeros(labels.shape)

        for i in range(labels.shape[1]):
            second_labels = labels[:, i].contiguous().view(-1, 1)

            mask = torch.eq(second_labels, second_labels.t()).float().to(device)

            # mask-out self-contrast cases
            logits_mask = torch.scatter(
                torch.ones_like(mask),
                1,
                torch.arange(batch_size).view(-1, 1).to(device),
                0
            )
            mask = mask * logits_mask
            single_samples = (mask.sum(1) == 0).float()

            # compute log_prob
            exp_logits = torch.exp(logits) * logits_mask

            log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-20)

            # compute mean of log-likelihood over positive
            # invoid to devide the zero
            mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + single_samples)

            # loss
            # filter those single sample
            loss = - mean_log_prob_pos * (1 - single_samples)
            loss = loss.sum() / (loss.shape[0] - single_samples.sum())

            minute_loss[:, i] = loss

        # loss_mean = minute_loss.mean(1).sum()
        loss_mean = minute_loss.mean()

        return loss_mean
