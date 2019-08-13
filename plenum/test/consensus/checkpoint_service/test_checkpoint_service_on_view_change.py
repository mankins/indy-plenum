import pytest

from plenum.common.messages.internal_messages import ViewChangeStarted, ViewChangeFinished, ApplyNewView
from plenum.common.messages.node_messages import Checkpoint
from plenum.server.consensus.checkpoint_service import CheckpointService
from plenum.test.consensus.helper import copy_shared_data, check_service_changed_only_owned_fields_in_shared_data, \
    create_new_view, create_checkpoints


def test_do_nothing_on_view_change_started(internal_bus, checkpoint_service):
    checkpoint_service._data.checkpoints.update(create_checkpoints(view_no=0))
    checkpoint_service._data.stable_checkpoint = 200
    checkpoint_service._data.low_watermark = 200
    checkpoint_service._data.high_watermark = checkpoint_service._data.low_watermark + 300
    old_data = copy_shared_data(checkpoint_service._data)

    internal_bus.send(ViewChangeStarted(view_no=4))

    new_data = copy_shared_data(checkpoint_service._data)
    assert old_data == new_data


@pytest.mark.parametrize('checkpoints, stable_checkpoint, checkpoints_result', [
    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')],
     100,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')]),

    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=0, digest='some')],
     0,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')]),

    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=100, digest='some')],
     0,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')]),

    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=100, digest='some')],
     100,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')]),

    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=100, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')],
     100,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some')]),

    ([Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=100, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=300, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=400, digest='some')],
     100,
     [Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=200, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=300, digest='some'),
      Checkpoint(instId=0, viewNo=3, seqNoStart=0, seqNoEnd=400, digest='some')]),

])
def test_update_shared_data_on_view_change_finished(internal_bus, checkpoint_service,
                                                    checkpoints, stable_checkpoint,
                                                    checkpoints_result):
    old_data = copy_shared_data(checkpoint_service._data)
    checkpoint_service._data.checkpoints.update(checkpoints)
    checkpoint_service._data.stable_checkpoint = stable_checkpoint
    checkpoint_service._data.low_watermark = stable_checkpoint
    checkpoint_service._data.high_watermark = checkpoint_service._data.low_watermark + 300

    initial_view_no = 3
    new_view = create_new_view(initial_view_no=initial_view_no, stable_cp=200)
    internal_bus.send(ViewChangeFinished(view_no=initial_view_no + 1,
                                         view_changes=new_view.viewChanges,
                                         checkpoint=new_view.checkpoint,
                                         batches=new_view.batches))

    new_data = copy_shared_data(checkpoint_service._data)
    check_service_changed_only_owned_fields_in_shared_data(CheckpointService, old_data, new_data)

    assert list(checkpoint_service._data.checkpoints) == checkpoints_result
    assert checkpoint_service._data.stable_checkpoint == 200
    assert checkpoint_service._data.low_watermark == 200
    assert checkpoint_service._data.high_watermark == checkpoint_service._data.low_watermark + 300


def test_do_nothing_on_apply_new_view(internal_bus, checkpoint_service):
    checkpoint_service._data.checkpoints.update(create_checkpoints(view_no=0))
    checkpoint_service._data.stable_checkpoint = 100
    checkpoint_service._data.low_watermark = 100
    checkpoint_service._data.high_watermark = checkpoint_service._data.low_watermark + 300
    old_data = copy_shared_data(checkpoint_service._data)

    initial_view_no = 3
    new_view = create_new_view(initial_view_no=initial_view_no, stable_cp=200)
    internal_bus.send(ApplyNewView(view_no=initial_view_no + 1,
                                   view_changes=new_view.viewChanges,
                                   checkpoint=new_view.checkpoint,
                                   batches=new_view.batches))

    new_data = copy_shared_data(checkpoint_service._data)
    assert old_data == new_data
